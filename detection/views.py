import os
import json
import logging
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from detection.services.detector import FakeNewsDetector
from detection.services.domain_analyzer import fetch_article_from_url, analyze_domain_credibility
from detection.models import IndexedNews, DetectionLog, Article
from apps.cms.models import NewsAndUpdate

logger = logging.getLogger(__name__)


def _calculate_directory_size_mb(path: str) -> float:
    """Calculate size of a directory in Megabytes."""
    total_bytes = 0
    if not os.path.exists(path):
        return 0.0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            try:
                total_bytes += os.path.getsize(fp)
            except OSError:
                pass
    return round(total_bytes / (1024 * 1024), 2)


@csrf_exempt
@require_http_methods(["POST"])
def detect_api_view(request):
    """
    POST /api/detect/
    Primary API endpoint for text-based fake news detection.
    Accepts JSON: {"content": "..."}
    Returns complete structured Credibility Report.
    """
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
        else:
            body = request.POST

        content = body.get('content', '') or body.get('text', '') or body.get('news', '')
        if not content or not str(content).strip():
            return JsonResponse({
                'success': False,
                'error': 'No content provided. Please submit text to verify.'
            }, status=400)

        report = FakeNewsDetector.detect(content=str(content).strip())
        return JsonResponse(report, status=200 if report.get('success') else 400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)
    except Exception as e:
        logger.error(f"Error in detect_api_view: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Internal detection processing error.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def detect_url_api_view(request):
    """
    POST /api/detect/url/
    URL-based detection endpoint with SSRF protection, content extraction,
    domain analysis, and credibility scoring.
    Accepts JSON: {"url": "https://..."}
    """
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
        else:
            body = request.POST

        url = body.get('url', '').strip()
        if not url:
            return JsonResponse({'success': False, 'error': 'Please provide an article URL.'}, status=400)

        report = FakeNewsDetector.detect(url=url)
        return JsonResponse(report, status=200 if report.get('success') else 400)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)
    except Exception as e:
        logger.error(f"Error in detect_url_api_view: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Unable to process article URL.'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def legacy_detect_view(request):
    """
    POST /detect/
    Backward-compatible detection endpoint.
    Maintains compatibility with legacy frontend and API clients while using
    the high-speed FTS5 + ensemble pipeline.
    """
    try:
        content = ""
        if request.content_type == 'application/json':
            try:
                body = json.loads(request.body)
                content = body.get('content', '') or body.get('text', '') or body.get('news', '')
            except Exception:
                pass
        if not content:
            content = request.POST.get('content', '') or request.POST.get('text', '') or request.POST.get('news', '')

        if not content or not str(content).strip():
            return JsonResponse({'error': 'No content provided'}, status=400)

        report = FakeNewsDetector.detect(content=str(content).strip())

        # Format backward compatible response
        legacy_response = {
            'result': report.get('result', 'Inconclusive'),
            'confidence': report.get('confidence', 50.0),
            'source': report.get('source', 'Ensemble Detector'),
            'evidence': report.get('evidence', {}),
            'models': report.get('models', {}).get('predictions', {}),
            'explanation': report.get('explanation', []),
            'why_real': report.get('why_real', []),
            'why_fake': report.get('why_fake', []),
            'ai_summary': report.get('ai_summary', ''),
            'ai_provider': report.get('ai_provider', ''),
            'sentiment_analysis': report.get('sentiment_analysis', {}),
            'factuality_metrics': report.get('factuality_metrics', {}),
            'objectivity_pct': report.get('objectivity_pct', 70),
            'journalistic_rigor': report.get('journalistic_rigor', 'Moderate'),
            'credibility_report': report
        }
        return JsonResponse(legacy_response)

    except Exception as e:
        logger.error(f"Error in legacy_detect_view: {e}", exc_info=True)
        return JsonResponse({'error': 'Unable to process detection request'}, status=500)


@require_http_methods(["GET"])
def system_stats_api(request):
    """
    GET /api/system/stats/
    Provides monitoring metrics for the admin dashboard:
    - Database size
    - Indexed news count (verified vs transient)
    - Total admin articles
    - ML model directory size
    - Recent detection query count
    """
    try:
        db_path = settings.DATABASES['default']['NAME']
        db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2) if os.path.exists(db_path) else 0.0

        model_dir = getattr(settings, 'ML_MODELS_DIR', os.path.join(settings.BASE_DIR, 'ml_models', 'current'))
        model_size_mb = _calculate_directory_size_mb(model_dir)

        total_indexed = IndexedNews.objects.count()
        verified_indexed = IndexedNews.objects.filter(is_verified=True).count()
        transient_indexed = total_indexed - verified_indexed

        total_articles = NewsAndUpdate.objects.count()
        total_detections = DetectionLog.objects.count()

        latest_detection = DetectionLog.objects.first()
        latest_detection_time = latest_detection.created_at.strftime('%Y-%m-%d %H:%M') if latest_detection else "None"

        latest_news = IndexedNews.objects.first()
        latest_news_time = latest_news.created_at.strftime('%Y-%m-%d %H:%M') if latest_news else "None"

        return JsonResponse({
            'success': True,
            'stats': {
                'indexed_articles': total_indexed,
                'verified_reference_news': verified_indexed,
                'transient_daily_news': transient_indexed,
                'user_articles': total_articles,
                'total_detections': total_detections,
                'db_size_mb': db_size_mb,
                'model_size_mb': model_size_mb,
                'last_detection_at': latest_detection_time,
                'last_ingest_at': latest_news_time,
                'retention_policy_days': 30
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving system stats: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Failed to retrieve system statistics.'}, status=500)


@require_http_methods(["GET"])
def detection_history_api(request):
    """
    GET /api/detections/history/
    Paginated audit log of detection queries for dashboard monitoring.
    Supports search query and verdict filtering.
    """
    try:
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(50, max(5, int(request.GET.get('page_size', 15))))
        verdict = request.GET.get('verdict', '').strip()
        search = request.GET.get('search', '').strip()

        qs = DetectionLog.objects.all().order_by('-created_at')

        if verdict and verdict.lower() != 'all':
            qs = qs.filter(result__icontains=verdict)

        if search:
            qs = qs.filter(query_text__icontains=search)

        total = qs.count()
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size

        logs = qs[start:end]
        items = []
        for log in logs:
            items.append({
                'id': log.id,
                'query_text': log.query_text,
                'input_type': log.input_type,
                'url': log.url,
                'result': log.result,
                'confidence': log.confidence,
                'source_info': log.source_info,
                'response_time_ms': log.response_time_ms,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'explanation': log.explanation,
                'evidence': log.evidence
            })

        return JsonResponse({
            'success': True,
            'total': total,
            'page': page,
            'total_pages': total_pages,
            'detections': items
        })
    except Exception as e:
        logger.error(f"Error retrieving detection history: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def source_check_api(request):
    """
    POST /api/source/check/
    Check the credibility and reputation of a news domain.
    Accepts JSON: {"url": "https://..."}  OR  {"domain": "example.com"}
    """
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
        else:
            body = request.POST

        url = body.get('url', '').strip()
        domain = body.get('domain', '').strip()

        if not url and not domain:
            return JsonResponse({'success': False, 'error': 'Provide a URL or domain name.'}, status=400)

        if url:
            result = fetch_article_from_url(url)
            domain = result.get('domain', domain)
            is_https = result.get('is_https', True)
        else:
            is_https = True  # Assume HTTPS when only domain is given

        analysis = analyze_domain_credibility(domain, is_https=is_https)

        # Enrich with detection stats from our logs
        url_count = DetectionLog.objects.filter(url__icontains=domain).count()
        fake_count = DetectionLog.objects.filter(url__icontains=domain, result__icontains='Fake').count()
        real_count = DetectionLog.objects.filter(url__icontains=domain, result__icontains='Real').count()

        analysis.update({
            'success': True,
            'domain_checked': domain,
            'detection_stats': {
                'total_checked': url_count,
                'real_count': real_count,
                'fake_count': fake_count,
                'fake_rate_pct': round((fake_count / url_count * 100), 1) if url_count else 0.0,
            }
        })
        return JsonResponse(analysis)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON payload.'}, status=400)
    except Exception as e:
        logger.error(f"Error in source_check_api: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': 'Unable to analyze source.'}, status=500)


@require_http_methods(["GET"])
def needs_review_api(request):
    """
    GET /api/detections/needs-review/
    Returns the queue of borderline detections awaiting human review.
    """
    try:
        qs = DetectionLog.objects.filter(needs_review=True, is_reviewed=False).order_by('-created_at')[:50]
        items = []
        for log in qs:
            items.append({
                'id': log.id,
                'query_text': log.query_text[:200],
                'result': log.result,
                'confidence': log.confidence,
                'bias_label': log.bias_label,
                'political_lean': log.political_lean,
                'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        return JsonResponse({'success': True, 'count': len(items), 'queue': items})
    except Exception as e:
        logger.error(f"Error retrieving review queue: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def review_detection_api(request, detection_id):
    """
    POST /api/detections/<id>/review/
    Human reviewer submits an override verdict for a borderline detection.
    Accepts JSON: {"verdict": "Real News"} or {"verdict": "Fake News"}
    """
    try:
        log = DetectionLog.objects.get(pk=detection_id)
    except DetectionLog.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Detection not found.'}, status=404)

    try:
        body = json.loads(request.body)
        reviewer_verdict = body.get('verdict', '').strip()
        if reviewer_verdict not in ('Real News', 'Fake News', 'Inconclusive'):
            return JsonResponse({'success': False, 'error': 'Invalid verdict. Use: Real News, Fake News, or Inconclusive.'}, status=400)

        log.reviewer_verdict = reviewer_verdict
        log.is_reviewed = True
        log.save(update_fields=['reviewer_verdict', 'is_reviewed'])

        return JsonResponse({
            'success': True,
            'message': f'Detection #{detection_id} marked as reviewed.',
            'reviewer_verdict': reviewer_verdict
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON.'}, status=400)
    except Exception as e:
        logger.error(f"Error in review_detection_api: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def articles_api(request):
    """
    GET  /api/articles/  -> List articles
    POST /api/articles/  -> Create new article
    """
    if request.method == 'GET':
        articles = Article.objects.all()
        data = []
        for art in articles:
            data.append({
                'id': art.id,
                'title': art.title,
                'username': art.username,
                'description': art.description,
                'rate': float(art.rate) if art.rate is not None else 5.0,
                'image': art.image.url if art.image else None,
                'created_at': art.created_at.strftime('%Y-%m-%d %H:%M:%S') if art.created_at else ''
            })
        return JsonResponse(data, safe=False)

    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body)
        else:
            body = request.POST

        art = Article.objects.create(
            title=body.get('title', 'Untitled'),
            username=body.get('username', 'Admin'),
            description=body.get('description', ''),
            rate=float(body.get('rate', 5.0) or 5.0),
        )
        return JsonResponse({
            'success': True,
            'id': art.id,
            'title': art.title,
            'message': 'Article created successfully.'
        }, status=201)
    except Exception as e:
        logger.error(f"Error creating article: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def article_detail_api(request, pk):
    """
    GET    /api/articles/<pk>/ -> Retrieve article
    PUT    /api/articles/<pk>/ -> Update article
    DELETE /api/articles/<pk>/ -> Delete article
    """
    try:
        art = Article.objects.get(pk=pk)
    except Article.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Article not found.'}, status=404)

    if request.method == 'DELETE':
        art.delete()
        return JsonResponse({'success': True, 'message': 'Article deleted.'})

    if request.method == 'PUT':
        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body)
            else:
                body = request.POST

            art.title = body.get('title', art.title)
            art.username = body.get('username', art.username)
            art.description = body.get('description', art.description)
            if 'rate' in body and body['rate'] is not None:
                art.rate = float(body['rate'])
            art.save()
            return JsonResponse({'success': True, 'message': 'Article updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({
        'id': art.id,
        'title': art.title,
        'username': art.username,
        'description': art.description,
        'rate': float(art.rate) if art.rate is not None else 5.0,
        'image': art.image.url if art.image else None,
        'created_at': art.created_at.strftime('%Y-%m-%d %H:%M:%S') if art.created_at else ''
    })


@csrf_exempt
@require_http_methods(["POST"])
def models_train_api(request):
    """
    POST /api/models/train/
    Trigger background training of ML models.
    """
    from detection.services.trainer import ModelTrainerState
    trainer = ModelTrainerState.get_instance()
    success, message = trainer.start_training()
    return JsonResponse({
        'success': success,
        'message': message,
        'status': trainer.status
    }, status=200 if success else 400)


@require_http_methods(["GET"])
def models_train_status_api(request):
    """
    GET /api/models/train/status/?since=0
    Poll live training execution status, elapsed running time, and stdout console stream.
    """
    from detection.services.trainer import ModelTrainerState
    since_idx = int(request.GET.get('since', 0))
    trainer = ModelTrainerState.get_instance()
    return JsonResponse(trainer.get_status_payload(since_index=since_idx))


@require_http_methods(["GET"])
def models_summary_api(request):
    """
    GET /api/models/summary/
    Detailed inventory of all active ML classifiers, FTS5 corpus,
    and individual fake/real counts and performance metrics.
    """
    total_indexed = IndexedNews.objects.count()
    real_indexed = IndexedNews.objects.filter(label='real').count()
    fake_indexed = IndexedNews.objects.filter(label='fake').count()

    total_detections = DetectionLog.objects.count()
    detections_real = DetectionLog.objects.filter(result__icontains='Real').count()
    detections_fake = DetectionLog.objects.filter(result__icontains='Fake').count()

    model_dir = getattr(settings, 'ML_MODELS_DIR', os.path.join(settings.BASE_DIR, 'ml_models', 'current'))
    model_size_mb = _calculate_directory_size_mb(model_dir)

    models_list = [
        {
            'id': 'logistic-regression',
            'name': 'Logistic Regression (L-BFGS)',
            'type': 'Linear Classifier + TF-IDF',
            'status': 'Active (Production)',
            'accuracy': 61.74,
            'f1_score': 59.99,
            'total_samples': 10240,
            'real_count': 5752,
            'fake_count': 4488,
            'features': 'TF-IDF (1-4 grams, 200k max vocab)',
            'artifact': 'final_model.sav',
            'is_primary': True
        },
        {
            'id': 'naive-bayes',
            'name': 'Multinomial Naive Bayes',
            'type': 'Probabilistic Classifier',
            'status': 'Active',
            'accuracy': 60.50,
            'f1_score': 58.90,
            'total_samples': 10240,
            'real_count': 5752,
            'fake_count': 4488,
            'features': 'Bag of Words (CountVectorizer)',
            'artifact': 'nb_model.pkl',
            'is_primary': False
        },
        {
            'id': 'linear-svm',
            'name': 'Linear Support Vector Machine (LinearSVC)',
            'type': 'Max-Margin Separator',
            'status': 'Active',
            'accuracy': 60.10,
            'f1_score': 58.20,
            'total_samples': 10240,
            'real_count': 5752,
            'fake_count': 4488,
            'features': 'Hinge Loss, L2 Regularization',
            'artifact': 'svm_model.pkl',
            'is_primary': False
        },
        {
            'id': 'random-forest',
            'name': 'Random Forest Classifier',
            'type': 'Ensemble Decision Trees',
            'status': 'Active',
            'accuracy': 59.40,
            'f1_score': 57.80,
            'total_samples': 10240,
            'real_count': 5752,
            'fake_count': 4488,
            'features': '100 Estimators, Gini Impurity',
            'artifact': 'rf_model.pkl',
            'is_primary': False
        },
        {
            'id': 'sgd-classifier',
            'name': 'SGD Classifier (Hinge/ElasticNet)',
            'type': 'Stochastic Gradient Descent',
            'status': 'Active',
            'accuracy': 59.80,
            'f1_score': 58.00,
            'total_samples': 10240,
            'real_count': 5752,
            'fake_count': 4488,
            'features': 'Adaptive Learning Rate',
            'artifact': 'sgd_logistic.pkl',
            'is_primary': False
        },
        {
            'id': 'fts5-benchmark',
            'name': 'FTS5 Benchmark News Corpus',
            'type': 'Exact & BM25 Full-Text Matcher',
            'status': 'Active (Ground Truth)',
            'accuracy': 98.00,
            'f1_score': 98.00,
            'total_samples': total_indexed,
            'real_count': real_indexed,
            'fake_count': fake_indexed,
            'features': 'SHA-256 Hash + SQLite FTS5 Index',
            'artifact': 'db.sqlite3 (news_index_fts)',
            'is_primary': True
        }
    ]

    return JsonResponse({
        'success': True,
        'summary': {
            'total_models': len(models_list),
            'total_dataset_samples': total_indexed,
            'total_real_count': real_indexed,
            'total_fake_count': fake_indexed,
            'total_audit_detections': total_detections,
            'detections_real': detections_real,
            'detections_fake': detections_fake,
            'model_directory_mb': model_size_mb,
        },
        'models': models_list
    })


@require_http_methods(["GET"])
def models_data_api(request):
    """
    GET /api/models/data/
    Server-side paginated and filtered dataset statements.
    Params:
      page (default 1)
      page_size (default 15)
      search (text query)
      label (all, real, fake)
      source (source name or all)
    """
    try:
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(100, max(5, int(request.GET.get('page_size', 15))))
        search = request.GET.get('search', '').strip()
        label_filter = request.GET.get('label', '').strip().lower()
        source_filter = request.GET.get('source', '').strip()

        qs = IndexedNews.objects.all().order_by('-created_at')

        if label_filter and label_filter != 'all':
            qs = qs.filter(label=label_filter)

        if search:
            from django.db.models import Q
            qs = qs.filter(Q(title__icontains=search) | Q(summary__icontains=search))

        if source_filter and source_filter != 'all':
            qs = qs.filter(source__icontains=source_filter)

        total_filtered = qs.count()
        total_pages = max(1, (total_filtered + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size

        # Precompute real/fake breakdown for the filtered query
        filtered_real = qs.filter(label='real').count()
        filtered_fake = qs.filter(label='fake').count()

        records = []
        for item in qs[start:end]:
            records.append({
                'id': item.id,
                'title': item.title,
                'summary': item.summary[:200] if item.summary else '',
                'label': item.label,
                'source': item.source,
                'is_verified': item.is_verified,
                'published_at': item.published_at.strftime('%Y-%m-%d') if item.published_at else None,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else None,
                'content_hash': item.content_hash[:16] + '...' if item.content_hash else ''
            })

        # Available unique sources for filter dropdown
        sources = list(
            IndexedNews.objects.values_list('source', flat=True)
            .distinct()[:20]
        )

        return JsonResponse({
            'success': True,
            'page': page,
            'page_size': page_size,
            'total': total_filtered,
            'total_pages': total_pages,
            'counts': {
                'total': total_filtered,
                'real': filtered_real,
                'fake': filtered_fake,
            },
            'sources': sources,
            'results': records
        })
    except Exception as e:
        logger.error(f"Error in models_data_api: {e}", exc_info=True)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


