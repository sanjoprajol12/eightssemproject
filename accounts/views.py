from django.http import HttpResponse
# from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect


def home(request):
    return render(request, "login.html")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Admin

# Show register React form
def register_template(request):
    return render(request, 'register.html')

# API to handle register POST
@csrf_exempt
def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == 'POST':
        data = json.loads(request.body)

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        note = data.get('note', '')
        address = data.get('address', '')

        # Check required fields
        if not name or not email or not password:
            return JsonResponse({'message': 'Name, email and password are required'}, status=400)

        if Admin.objects.filter(email=email).exists():
            return JsonResponse({'message': 'Email already registered'}, status=400)

        from django.contrib.auth.hashers import make_password
        Admin.objects.create(
            name=name,
            email=email,
            password=make_password(password),
            phone=phone,
            note=note,
            address=address
        )
        return JsonResponse({'message': 'Registration successful'})

    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        import hmac
        from django.contrib.auth.hashers import check_password, make_password
        data = json.loads(request.body)

        email = data.get('email')
        password = data.get('password')

        # Check required fields
        if not email or not password:
            return JsonResponse({'message': 'Email and password are required'}, status=400)

        try:
            user = Admin.objects.get(email=email)
            is_valid = False
            # Check hashed password first
            if check_password(password, user.password):
                is_valid = True
            # Fallback to constant-time plaintext comparison for legacy accounts, auto-upgrade
            elif hmac.compare_digest(str(user.password), str(password)):
                is_valid = True
                user.password = make_password(password)
                user.save(update_fields=['password'])

            if is_valid:
                request.session['admin_id'] = user.id  # set session
                return JsonResponse({'message': 'Login successful', 'name': user.name})
            else:
                return JsonResponse({'message': 'Invalid email or password'}, status=401)
        except Admin.DoesNotExist:
            return JsonResponse({'message': 'Invalid email or password'}, status=401)

    return JsonResponse({'message': 'Invalid request'}, status=400)


def index(request):
    return render(request, 'index.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Admin, Article
import json
import base64
import uuid

@ensure_csrf_cookie
def dashboard_view(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('login')

    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return redirect('login')

    return render(request, 'dashboard.html', {
        'admin': admin,
        'csrf_token': request.COOKIES.get('csrftoken'),
    })

@csrf_exempt
def articles_json(request):
    """Handle GET (fetch articles) and POST (create article) requests"""
    if request.method == 'GET':
        articles = Article.objects.all().order_by('-created_at')
        data = [
            {
                'id': a.id,
                'title': a.title,
                'description': a.description,
                'image': a.image.url if a.image else '',
                'username': a.username,
                'rate': str(a.rate),
                'created_at': a.created_at.strftime('%Y-%m-%d %H:%M'),
                'category': 'General',
            }
            for a in articles
        ]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                # Handle file upload via form data
                title = request.POST.get('title')
                description = request.POST.get('description', '')
                username = request.POST.get('username')
                rate = request.POST.get('rate', 0.0)
                category = request.POST.get('category', 'General')
                image = request.FILES.get('image')
            else:
                # Handle JSON data with base64 encoded image
                data = json.loads(request.body)
                title = data.get('title')
                description = data.get('description', '')
                username = data.get('username')
                rate = data.get('rate', 0.0)
                category = data.get('category', 'General')
                image_data = data.get('image')  # base64 encoded image
                image = None
                
                if image_data and image_data.startswith('data:image'):
                    # Parse base64 image
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_name = f"{uuid.uuid4()}.{ext}"
                    image = ContentFile(base64.b64decode(imgstr), name=image_name)

            if not title or not username:
                return JsonResponse({'error': 'Title and username are required'}, status=400)

            admin_id = request.session.get('admin_id')
            if not admin_id:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            admin = get_object_or_404(Admin, id=admin_id)

            article = Article.objects.create(
                title=title,
                description=description,
                username=username,
                rate=rate,
                admin=admin,
                image=image
            )
            
            return JsonResponse({
                'message': 'Article created successfully',
                'article': {
                    'id': article.id,
                    'title': article.title,
                    'description': article.description,
                    'image': article.image.url if article.image else '',
                    'username': article.username,
                    'rate': str(article.rate),
                    'created_at': article.created_at.strftime('%Y-%m-%d %H:%M'),
                    'category': category
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def article_detail(request, article_id):
    """Handle individual article operations"""
    try:
        article = get_object_or_404(Article, id=article_id)
    except Article.DoesNotExist:
        return JsonResponse({'error': 'Article not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': article.id,
            'title': article.title,
            'description': article.description,
            'image': article.image.url if article.image else '',
            'username': article.username,
            'rate': str(article.rate),
            'created_at': article.created_at.strftime('%Y-%m-%d %H:%M'),
            'category': 'General'
        })

    elif request.method == 'PUT':
        try:
            # Check if user is authenticated
            admin_id = request.session.get('admin_id')
            if not admin_id:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            # Handle both JSON and multipart form data
            if request.content_type.startswith('multipart/form-data'):
                title = request.POST.get('title')
                description = request.POST.get('description', '')
                username = request.POST.get('username')
                rate = request.POST.get('rate', article.rate)
                new_image = request.FILES.get('image')
            else:
                data = json.loads(request.body)
                title = data.get('title', article.title)
                description = data.get('description', article.description)
                username = data.get('username', article.username)
                rate = data.get('rate', article.rate)
                image_data = data.get('image')
                new_image = None

                if image_data and image_data.startswith('data:image'):
                    # Parse base64 image
                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_name = f"{uuid.uuid4()}.{ext}"
                    new_image = ContentFile(base64.b64decode(imgstr), name=image_name)

            # Update article fields
            article.title = title
            article.description = description
            article.username = username
            article.rate = rate

            # Handle image update
            if new_image:
                # Delete old image if it exists
                if article.image:
                    try:
                        default_storage.delete(article.image.name)
                    except:
                        pass
                article.image = new_image

            article.save()

            return JsonResponse({
                'message': 'Article updated successfully',
                'article': {
                    'id': article.id,
                    'title': article.title,
                    'description': article.description,
                    'image': article.image.url if article.image else '',
                    'username': article.username,
                    'rate': str(article.rate),
                    'created_at': article.created_at.strftime('%Y-%m-%d %H:%M'),
                    'category': 'General'
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        try:
            # Check if user is authenticated
            admin_id = request.session.get('admin_id')
            if not admin_id:
                return JsonResponse({'error': 'Authentication required'}, status=401)

            
            # Delete associated image file
            if article.image:
                try:
                    default_storage.delete(article.image.name)
                except:
                    pass

            article.delete()
            return JsonResponse({'message': 'Article deleted successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

# Duplicate article_detail removed — the full implementation above (lines ~196–299) handles GET, PUT, and DELETE.


def admin_edit(request, admin_id):
    admin = get_object_or_404(Admin, id=admin_id)
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = AdminForm(instance=admin)
    return render(request, 'admin_edit.html', {'form': form, 'admin': admin})

def admin_delete(request, admin_id):
    admin = get_object_or_404(Admin, id=admin_id)
    if request.method == 'POST':
        admin.delete()
        return redirect('dashboard')
    return render(request, 'admin_delete_confirm.html', {'admin': admin})


@csrf_exempt
def profile_api(request):
    """API endpoint to get and update current authenticated admin profile"""
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return JsonResponse({'error': 'Admin not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': admin.id,
            'name': admin.name,
            'email': admin.email,
            'phone': admin.phone or '',
            'address': admin.address or '',
            'note': admin.note or '',
        })

    elif request.method in ['POST', 'PUT']:
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            name = data.get('name', '').strip()
            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            admin.name = name
            admin.phone = data.get('phone', admin.phone or '').strip()
            admin.address = data.get('address', admin.address or '').strip()
            admin.note = data.get('note', admin.note or '').strip()

            new_password = data.get('password')
            if new_password and str(new_password).strip():
                from django.contrib.auth.hashers import make_password
                admin.password = make_password(str(new_password).strip())

            admin.save()
            return JsonResponse({
                'message': 'Profile updated successfully',
                'admin': {
                    'id': admin.id,
                    'name': admin.name,
                    'email': admin.email,
                    'phone': admin.phone or '',
                    'address': admin.address or '',
                    'note': admin.note or '',
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)




def logout_view(request):
    request.session.flush()
    return redirect('/')

import os
import json
import pickle
import threading
import numpy as np
import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from accounts.models import Article

# ✅ Import your cleaner
from accounts.utils.text_cleaning import clean_text

# Module-level cache to avoid reloading large datasets on every request
_DATA_CACHE = {
    'loaded': False,
    'texts': None,
    'tfidf_matrix': None,
    'row_norms': None,
    'lock': threading.Lock()
}

def _ensure_dataset_matrix(tfidf):
    """Load `True.csv` and LIAR `train.tsv` texts, transform with provided tfidf,
    compute row norms and cache the sparse matrix for fast similarity queries."""
    if _DATA_CACHE['loaded']:
        return

    with _DATA_CACHE['lock']:
        if _DATA_CACHE['loaded']:
            return

        base = settings.BASE_DIR
        texts = []

        # Load True.csv (combine title and text where available)
        true_path = os.path.join(base, 'True.csv')
        if os.path.exists(true_path):
            try:
                df_true = pd.read_csv(true_path, low_memory=False)
                # prefer 'title' + 'text' if available
                if 'title' in df_true.columns and 'text' in df_true.columns:
                    combined = (df_true['title'].fillna('') + ' ' + df_true['text'].fillna('')).astype(str)
                elif 'title' in df_true.columns:
                    combined = df_true['title'].fillna('').astype(str)
                else:
                    combined = df_true.iloc[:, 0].fillna('').astype(str)

                texts.extend(combined[combined.str.strip().astype(bool)].tolist())
            except Exception:
                pass

        # Load LIAR train.tsv (column 2 is the statement text in the LIAR dataset)
        liar_path = os.path.join(base, 'train.tsv')
        if os.path.exists(liar_path):
            try:
                liar = pd.read_csv(liar_path, sep='\t', header=None, quoting=3, low_memory=False)
                if liar.shape[1] > 2:
                    liar_texts = liar[2].fillna('').astype(str)
                else:
                    liar_texts = liar.iloc[:, -1].fillna('').astype(str)
                texts.extend(liar_texts[liar_texts.str.strip().astype(bool)].tolist())
            except Exception:
                pass

        # Finalize
        if not texts:
            # nothing to cache
            _DATA_CACHE['texts'] = []
            _DATA_CACHE['tfidf_matrix'] = None
            _DATA_CACHE['row_norms'] = None
            _DATA_CACHE['loaded'] = True
            return

        # Transform texts using the provided tfidf (this may take time once)
        mat = tfidf.transform(texts)

        # Precompute row norms for cosine similarity (||row||)
        # mat.multiply(mat).sum(axis=1) returns a (n,1) matrix
        row_sq = mat.multiply(mat).sum(axis=1)
        row_norms = np.sqrt(np.array(row_sq).reshape(-1))

        _DATA_CACHE['texts'] = texts
        _DATA_CACHE['tfidf_matrix'] = mat
        _DATA_CACHE['row_norms'] = row_norms
        _DATA_CACHE['loaded'] = True



@csrf_exempt
# def detect_fake_news(request):
#     if request.method == 'POST':
        # try:
        #     content = json.loads(request.body).get('content', '').strip()
        #     if not content:
        #         return JsonResponse({'error': 'No content provided'}, status=400)
            
        #     cleaned_content = clean_text(content)

        #     # 1️⃣ Check Article table by title only
        #     article_match = Article.objects.filter(title__iexact=content).first()
        #     if article_match:
        #         # If title exists in Article table, consider it True
        #         return JsonResponse({'result': "Real News", 'source': 'Article Table (title match)'})

        #     # 2️⃣ Fallback to ML prediction
        #     model_dir = os.path.join(settings.BASE_DIR, 'accounts', 'ml_models')
        #     tfidf = pickle.load(open(os.path.join(model_dir, 'tfidf.pkl'), 'rb'))
        #     voting_model = pickle.load(open(os.path.join(model_dir, 'voting_model.pkl'), 'rb'))
        #     vector = tfidf.transform([cleaned_content])
        #     pred = voting_model.predict(vector)[0]

        #     result_text = "Real News" if pred == 1 else "Fake News"

        #     return JsonResponse({'result': result_text, 'source': 'ML Model'})

        # except Exception as e:
        #     return JsonResponse({'error': str(e)}, status=500)

#     return JsonResponse({'error': 'Invalid request method'}, status=405)
@csrf_exempt
def detect_fake_news(request):
    """POST endpoint: classify input text as Real/Fake.

    Logic:
    - Load TF-IDF vectorizer + LR/NB/RF models from `accounts/ml_models`.
    - Cache TF-IDF vectors for `True.csv` and `test.tsv` (first call may be slow).
    - Compute cosine similarity between input and dataset texts; if max similarity >= 0.8
      AND at least one of LogisticRegression/NaiveBayes predicts real (1), return Real News.
    - Also accept Real if there's a partial title match in the `Article` table and a model predicts real.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
       
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        if not content or not str(content).strip():
            return JsonResponse({'error': 'No content provided'}, status=400)

        cleaned_content = clean_text(str(content).strip())

        # 1️⃣ Check Article table by title only (case-insensitive exact match)
        # If the submitted content exactly matches an Article title, return Real immediately.
        try:
            article_match = Article.objects.filter(title__iexact=str(content).strip()).first()
            if article_match:
                return JsonResponse({'result': 'Real News', 'source': 'Article Table (title exact match)'} )
        except Exception:
            # If DB access fails for any reason, continue with ML-based checks
            pass

        # Local imports to avoid depending on module-level state
        import os
        import pickle
        import numpy as np
        import pandas as pd
        from django.conf import settings

        model_dir = os.path.join(settings.BASE_DIR, 'accounts', 'ml_models')

        # Load vectorizer and models (optional models may be missing)
        try:
            tfidf = pickle.load(open(os.path.join(model_dir, 'tfidf.pkl'), 'rb'))
        except Exception as e:
            return JsonResponse({'error': 'Could not load tfidf.pkl', 'detail': str(e)}, status=500)

        def _maybe_load(name):
            p = os.path.join(model_dir, name)
            if os.path.exists(p):
                try:
                    return pickle.load(open(p, 'rb'))
                except Exception:
                    return None
            return None

        lr = _maybe_load('lr_model.pkl')
        nb = _maybe_load('nb_model.pkl')
        rf = _maybe_load('rf_model.pkl')
        voting = _maybe_load('voting_model.pkl')

        # Cache dataset TF-IDF matrix on the function to reuse between requests
        cache = getattr(detect_fake_news, '_cache', None)
        if cache is None:
            cache = {'texts': None, 'mat': None, 'norms': None}

        if cache['mat'] is None:
            texts = []
            base = settings.BASE_DIR

            # Load True.csv
            true_path = os.path.join(base, 'True.csv')
            if os.path.exists(true_path):
                try:
                    df_true = pd.read_csv(true_path, low_memory=False)
                    if 'title' in df_true.columns and 'text' in df_true.columns:
                        combined = (df_true['title'].fillna('') + ' ' + df_true['text'].fillna('')).astype(str)
                    elif 'title' in df_true.columns:
                        combined = df_true['title'].fillna('').astype(str)
                    else:
                        combined = df_true.iloc[:, 0].fillna('').astype(str)
                    texts.extend(combined[combined.str.strip().astype(bool)].tolist())
                except Exception:
                    pass

            # Load LIAR datasets: train.tsv, test.tsv, valid.tsv (statements in col 2)
            for lname in ('train.tsv', 'test.tsv', 'valid.tsv'):
                lpath = os.path.join(base, lname)
                if os.path.exists(lpath):
                    try:
                        df_l = pd.read_csv(lpath, sep='\t', header=None, quoting=3, low_memory=False)
                        if df_l.shape[1] > 2:
                            statements = df_l[2].fillna('').astype(str)
                        else:
                            statements = df_l.iloc[:, -1].fillna('').astype(str)
                        texts.extend(statements[statements.str.strip().astype(bool)].tolist())
                    except Exception:
                        pass

            # If no texts found, set empty cache
            if not texts:
                cache = {'texts': [], 'mat': None, 'norms': None}
            else:
                mat = tfidf.transform(texts)
                row_sq = mat.multiply(mat).sum(axis=1)
                norms = np.sqrt(np.array(row_sq).reshape(-1))
                cache = {'texts': texts, 'mat': mat, 'norms': norms}

            detect_fake_news._cache = cache

        # Vectorize input
        input_vec = tfidf.transform([cleaned_content])

        max_sim = 0.0
        matched_text = None
        exact_match = False
        matched_source = None
        # quick exact match check (case-insensitive) against cached texts
        if cache.get('texts'):
            try:
                low_text = cleaned_content.lower().strip()
                for t in cache['texts']:
                    if not t:
                        continue
                    if low_text == t.lower().strip():
                        exact_match = True
                        matched_text = t
                        matched_source = 'dataset_exact'
                        break
            except Exception:
                exact_match = False
        if cache['mat'] is not None:
            try:
                dots = cache['mat'].dot(input_vec.T).toarray().reshape(-1)
                vnorm = np.sqrt(input_vec.multiply(input_vec).sum())
                if vnorm == 0:
                    vnorm = 1e-9
                denom = cache['norms'] * vnorm
                denom[denom == 0] = 1e-9
                sims = dots / denom
                idx = int(np.argmax(sims))
                max_sim = float(sims[idx])
                if max_sim > 0:
                    matched_text = cache['texts'][idx]
            except Exception:
                max_sim = 0.0

        # Predictions from LR, NB, RF (and fallback to incremental models if available)
        preds = {'logistic_regression': None, 'naive_bayes': None, 'random_forest': None}
        try:
            if lr is not None:
                preds['logistic_regression'] = int(lr.predict(input_vec)[0])
        except Exception:
            preds['logistic_regression'] = None
        try:
            if nb is not None:
                preds['naive_bayes'] = int(nb.predict(input_vec)[0])
        except Exception:
            preds['naive_bayes'] = None
        try:
            if rf is not None:
                preds['random_forest'] = int(rf.predict(input_vec)[0])
        except Exception:
            preds['random_forest'] = None


        # DB partial title match
        db_partial = Article.objects.filter(title__icontains=cleaned_content).exists()

        # 2️⃣ Check Fake.csv for exact/similarity match
        fake_exact_match = False
        fake_similarity_ok = False
        fake_matched_text = None
        fake_source = None

        fake_path = os.path.join(settings.BASE_DIR, 'Fake.csv')
        if os.path.exists(fake_path):
            try:
                df_fake = pd.read_csv(fake_path, low_memory=False)
                fake_texts = []
                
                if 'title' in df_fake.columns and 'text' in df_fake.columns:
                    combined = (df_fake['title'].fillna('') + ' ' + df_fake['text'].fillna('')).astype(str)
                elif 'title' in df_fake.columns:
                    combined = df_fake['title'].fillna('').astype(str)
                else:
                    combined = df_fake.iloc[:, 0].fillna('').astype(str)
                
                fake_texts = combined[combined.str.strip().astype(bool)].tolist()
                
                # Check exact match (case-insensitive)
                low_content = cleaned_content.lower().strip()
                for ft in fake_texts:
                    if not ft:
                        continue
                    if low_content == ft.lower().strip():
                        fake_exact_match = True
                        fake_matched_text = ft
                        fake_source = 'Fake.csv Exact Match'
                        break
                
                # If no exact match, check similarity
                if not fake_exact_match and fake_texts:
                    try:
                        fake_mat = tfidf.transform(fake_texts)
                        fake_dots = fake_mat.dot(input_vec.T).toarray().reshape(-1)
                        fake_denom = np.sqrt(fake_mat.multiply(fake_mat).sum(axis=1).A1) * (np.sqrt(input_vec.multiply(input_vec).sum()) or 1e-9)
                        fake_denom[fake_denom == 0] = 1e-9
                        fake_sims = fake_dots / fake_denom
                        fake_max_sim = float(np.max(fake_sims))
                        fake_idx = int(np.argmax(fake_sims))
                        
                        if fake_max_sim >= 0.8:
                            fake_similarity_ok = True
                            fake_matched_text = fake_texts[fake_idx]
                            fake_source = 'Fake.csv Similarity Match'
                    except Exception:
                        pass
            except Exception:
                pass

        # Decision logic (STRICT): 
        # 1. If title matches Fake.csv exactly or with high similarity, return Fake News.
        # 2. Otherwise, only label Real if dataset or DB matches.
        # Models are returned for debugging but DO NOT determine the final label.
        similarity_ok = (max_sim >= 0.8)

        if fake_exact_match or fake_similarity_ok:
            result = 'Fake News'
            source = fake_source
        elif exact_match:
            result = 'Real News'
            source = 'Dataset Exact Match (True.csv)'
        elif similarity_ok:
            result = 'Real News'
            source = 'Dataset Similarity Match (True.csv)'
        elif db_partial:
            result = 'Real News'
            source = 'DB Partial Match'
        else:
            # If no dataset or DB match, default to Fake (models are only informational)
            result = 'Fake News'
            source = 'No Dataset/DB Match'

        # Convert model predictions to readable labels
        lr_result = 'Real News' if preds['logistic_regression'] == 1 else ('Fake News' if preds['logistic_regression'] == 0 else 'Unknown')
        nb_result = 'Real News' if preds['naive_bayes'] == 1 else ('Fake News' if preds['naive_bayes'] == 0 else 'Unknown')

        # Format detailed message with all results
        detailed_message = (
            f"📰 Final Result: {result}\n"
            f"Source: {source}\n\n"
            f"🔵 Logistic Regression: {lr_result}\n"
            f"🟠 Naive Bayes: {nb_result}"
        )

        return JsonResponse({
            'result': result,
            'source': source,
            'detailed_message': detailed_message,
            'logistic_regression': {
                'prediction': lr_result,
                'confidence': preds['logistic_regression']
            },
            'naive_bayes': {
                'prediction': nb_result,
                'confidence': preds['naive_bayes']
            },
            'predictions': preds,
            'similarity': {'max': round(max_sim, 4), 'matched_text': matched_text, 'threshold': 0.8},
            'fake_match': {'exact': fake_exact_match, 'similarity': fake_similarity_ok, 'matched_text': fake_matched_text},
            'db_partial_match': db_partial
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
