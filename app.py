from flask import Flask, render_template, jsonify, request
import os
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv
from services.serpapi_client import SerpAPIClient, SerpAPIError

# Load environment variables
load_dotenv()

# Configure comprehensive logging
def setup_logging():
    """Configure application logging with proper formatting and handlers."""
    # Configure root logger for serverless environment (no file logging)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Only console logging for serverless
        ]
    )
    
    # Set specific log levels for different components
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask request logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)   # Reduce HTTP client logs
    
    return logging.getLogger(__name__)

# Setup logging
logger = setup_logging()

# Create Flask application
app = Flask(__name__)

# Configure Flask error handling
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors with user-friendly response."""
    logger.warning(f"404 error: {request.url}")
    return jsonify({
        "success": False,
        "error": "Resource not found",
        "message": "The requested resource could not be found",
        "status_code": 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with logging and user-friendly response."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred. Please try again later.",
        "status_code": 500
    }), 500

@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle any unexpected exceptions."""
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return jsonify({
        "success": False,
        "error": "Unexpected error",
        "message": "An unexpected error occurred. Please contact support if this persists.",
        "status_code": 500
    }), 500

# Configure Flask for concurrent request handling
app.config['DEBUG'] = True
app.config['THREADED'] = True  # Enable threading for concurrent requests
app.config['PROCESSES'] = 1    # Use threading instead of multiprocessing
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Configure request timeout and connection pooling
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# Thread-safe request counter and connection pool
request_counter = threading.local()
connection_pool = ThreadPoolExecutor(max_workers=10)

@app.before_request
def before_request():
    """Initialize request-specific data and rate limiting"""
    if not hasattr(request_counter, 'count'):
        request_counter.count = 0
    request_counter.count += 1
    request_counter.start_time = time.time()

@app.after_request
def after_request(response):
    """Log request completion and add CORS headers for concurrent access"""
    if hasattr(request_counter, 'start_time'):
        duration = time.time() - request_counter.start_time
        app.logger.info(f"Request completed in {duration:.3f}s")
    
    # Add CORS headers for concurrent client requests
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    
    return response

@app.route('/')
def dashboard():
    """Main dashboard route serving the complete UI with error handling"""
    request_id = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"[{request_id}] Serving dashboard")
    
    try:
        # Check if required environment variables are set
        missing_config = []
        if not os.getenv('SERPAPI_KEY'):
            missing_config.append('SERPAPI_KEY')
        if not os.getenv('PLACE_ID'):
            missing_config.append('PLACE_ID')
        
        # Pass configuration status to template
        config_status = {
            'has_api_key': bool(os.getenv('SERPAPI_KEY')),
            'has_place_id': bool(os.getenv('PLACE_ID')),
            'missing_config': missing_config,
            'request_id': request_id
        }
        
        logger.info(f"[{request_id}] Dashboard served successfully")
        return render_template('dashboard.html', config=config_status)
        
    except Exception as e:
        logger.error(f"[{request_id}] Error serving dashboard: {str(e)}", exc_info=True)
        # Return a basic error page if template rendering fails
        return f"""
        <html>
        <head><title>Dashboard Error</title></head>
        <body>
        <h1>Dashboard Temporarily Unavailable</h1>
        <p>We're experiencing technical difficulties. Please try again later.</p>
        <p>Request ID: {request_id}</p>
        </body>
        </html>
        """, 500

@app.route('/api/reviews')
def get_reviews():
    """API endpoint for raw review data with comprehensive error handling"""
    request_id = f"reviews_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"[{request_id}] Processing reviews request")
    
    try:
        # Get and validate pagination parameters
        try:
            start = request.args.get('start', 0, type=int)
            num_reviews = request.args.get('num', 100, type=int)
        except (ValueError, TypeError) as e:
            logger.warning(f"[{request_id}] Invalid parameter format: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Invalid parameters",
                "message": "Parameters must be valid integers",
                "request_id": request_id
            }), 400
        
        # Validate parameter ranges
        if start < 0:
            logger.warning(f"[{request_id}] Invalid start parameter: {start}")
            return jsonify({
                "success": False,
                "error": "Invalid start parameter",
                "message": "Start parameter must be non-negative",
                "request_id": request_id
            }), 400
            
        if num_reviews <= 0 or num_reviews > 1000:
            logger.warning(f"[{request_id}] Invalid num_reviews parameter: {num_reviews}")
            return jsonify({
                "success": False,
                "error": "Invalid num_reviews parameter",
                "message": "Number of reviews must be between 1 and 1000",
                "request_id": request_id
            }), 400
        
        # Check environment configuration
        if not os.getenv('SERPAPI_KEY'):
            logger.error(f"[{request_id}] Missing SERPAPI_KEY configuration")
            return jsonify({
                "success": False,
                "error": "Configuration error",
                "message": "API service is not properly configured",
                "request_id": request_id
            }), 503
        
        if not os.getenv('PLACE_ID'):
            logger.error(f"[{request_id}] Missing PLACE_ID configuration")
            return jsonify({
                "success": False,
                "error": "Configuration error", 
                "message": "Restaurant place ID is not configured",
                "request_id": request_id
            }), 503
        
        # Initialize SerpAPI client and fetch reviews
        try:
            with SerpAPIClient() as client:
                logger.info(f"[{request_id}] Fetching reviews (start={start}, num={num_reviews})")
                review_data = client.fetch_reviews(start=start, num_reviews=num_reviews)
                
                # Validate response data
                if not review_data or not isinstance(review_data, dict):
                    logger.error(f"[{request_id}] Invalid response data from SerpAPI")
                    return jsonify({
                        "success": False,
                        "error": "Data validation error",
                        "message": "Invalid response from review service",
                        "request_id": request_id
                    }), 502
                
                reviews_count = len(review_data.get('reviews', []))
                logger.info(f"[{request_id}] Successfully fetched {reviews_count} reviews")
                
                return jsonify({
                    "success": True,
                    "data": review_data,
                    "pagination": {
                        "start": start,
                        "requested": num_reviews,
                        "returned": reviews_count
                    },
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
        except SerpAPIError as e:
            error_msg = str(e)
            logger.error(f"[{request_id}] SerpAPI error: {error_msg}")
            
            # Provide specific error messages based on error type
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                return jsonify({
                    "success": False,
                    "error": "Authentication error",
                    "message": "API authentication failed. Please check configuration.",
                    "request_id": request_id
                }), 401
            elif "rate limit" in error_msg.lower():
                return jsonify({
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again in a few minutes.",
                    "request_id": request_id,
                    "retry_after": 300  # 5 minutes
                }), 429
            elif "timeout" in error_msg.lower():
                return jsonify({
                    "success": False,
                    "error": "Request timeout",
                    "message": "The request took too long to complete. Please try again.",
                    "request_id": request_id
                }), 504
            else:
                return jsonify({
                    "success": False,
                    "error": "API integration error",
                    "message": "Unable to fetch reviews at this time. Please try again later.",
                    "request_id": request_id
                }), 503
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in get_reviews: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred while fetching reviews",
            "request_id": request_id
        }), 500

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for aggregated statistics with comprehensive error handling"""
    request_id = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"[{request_id}] Processing metrics request")
    
    try:
        # Get and validate query parameters
        try:
            start = request.args.get('start', 0, type=int)
            num_reviews = request.args.get('num', 100, type=int)
            interval = request.args.get('interval', 'monthly')
        except (ValueError, TypeError) as e:
            logger.warning(f"[{request_id}] Invalid parameter format: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Invalid parameters",
                "message": "Parameters must be valid integers and strings",
                "request_id": request_id
            }), 400
        
        # Validate parameter ranges and values
        if start < 0:
            logger.warning(f"[{request_id}] Invalid start parameter: {start}")
            return jsonify({
                "success": False,
                "error": "Invalid start parameter",
                "message": "Start parameter must be non-negative",
                "request_id": request_id
            }), 400
            
        if num_reviews <= 0 or num_reviews > 1000:
            logger.warning(f"[{request_id}] Invalid num_reviews parameter: {num_reviews}")
            return jsonify({
                "success": False,
                "error": "Invalid num_reviews parameter",
                "message": "Number of reviews must be between 1 and 1000",
                "request_id": request_id
            }), 400
            
        if interval not in ['daily', 'weekly', 'monthly']:
            logger.warning(f"[{request_id}] Invalid interval parameter: {interval}")
            return jsonify({
                "success": False,
                "error": "Invalid interval parameter",
                "message": "Interval must be 'daily', 'weekly', or 'monthly'",
                "request_id": request_id
            }), 400
        
        # Import services with error handling
        try:
            from services.data_processor import DataProcessor
        except ImportError as e:
            logger.error(f"[{request_id}] Failed to import DataProcessor: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Service unavailable",
                "message": "Data processing service is not available",
                "request_id": request_id
            }), 503
        
        # Fetch raw review data
        try:
            with SerpAPIClient() as client:
                logger.info(f"[{request_id}] Fetching review data for metrics")
                review_data = client.fetch_reviews(start=start, num_reviews=num_reviews)
        except SerpAPIError as e:
            logger.error(f"[{request_id}] SerpAPI error: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Data retrieval error",
                "message": "Unable to fetch review data for analysis",
                "request_id": request_id
            }), 503
        
        # Process the data with error handling
        try:
            processor = DataProcessor()
            transformed_reviews = processor.transform_review_data(review_data.get('reviews', []))
            
            if not transformed_reviews:
                logger.info(f"[{request_id}] No reviews available for analysis")
                return jsonify({
                    "success": True,
                    "data": {
                        "overall_metrics": processor.calculate_overall_metrics([]),
                        "rating_trends": [],
                        "volume_data": [],
                        "themes": []
                    },
                    "message": "No reviews available for analysis",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"[{request_id}] Processing {len(transformed_reviews)} reviews")
            
            # Calculate various metrics with individual error handling
            metrics_data = {}
            
            try:
                metrics_data["overall_metrics"] = processor.calculate_overall_metrics(transformed_reviews)
            except Exception as e:
                logger.error(f"[{request_id}] Error calculating overall metrics: {str(e)}")
                metrics_data["overall_metrics"] = {"error": "Failed to calculate overall metrics"}
            
            try:
                metrics_data["rating_trends"] = processor.aggregate_ratings_by_time(transformed_reviews, interval)
            except Exception as e:
                logger.error(f"[{request_id}] Error calculating rating trends: {str(e)}")
                metrics_data["rating_trends"] = []
            
            try:
                metrics_data["volume_data"] = processor.calculate_review_volume(transformed_reviews, interval)
            except Exception as e:
                logger.error(f"[{request_id}] Error calculating volume data: {str(e)}")
                metrics_data["volume_data"] = []
            
            try:
                metrics_data["themes"] = processor.extract_themes(transformed_reviews)
            except Exception as e:
                logger.error(f"[{request_id}] Error extracting themes: {str(e)}")
                metrics_data["themes"] = []
            
            # Check if any critical metrics failed
            if "error" in metrics_data.get("overall_metrics", {}):
                logger.warning(f"[{request_id}] Critical metrics calculation failed")
                return jsonify({
                    "success": False,
                    "error": "Metrics calculation error",
                    "message": "Unable to calculate key metrics from review data",
                    "request_id": request_id
                }), 500
            
            logger.info(f"[{request_id}] Successfully calculated metrics")
            
            return jsonify({
                "success": True,
                "data": {
                    **metrics_data,
                    "interval": interval,
                    "total_processed": len(transformed_reviews)
                },
                "metadata": review_data.get('metadata', {}),
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[{request_id}] Error processing review data: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Data processing error",
                "message": "Unable to process review data for metrics calculation",
                "request_id": request_id
            }), 500
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in get_metrics: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred while calculating metrics",
            "request_id": request_id
        }), 500

@app.route('/api/sentiment')
def get_sentiment():
    """API endpoint for sentiment analysis results with comprehensive error handling"""
    request_id = f"sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    logger.info(f"[{request_id}] Processing sentiment analysis request")
    
    try:
        # Get and validate query parameters
        try:
            start = request.args.get('start', 0, type=int)
            num_reviews = request.args.get('num', 100, type=int)
        except (ValueError, TypeError) as e:
            logger.warning(f"[{request_id}] Invalid parameter format: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Invalid parameters",
                "message": "Parameters must be valid integers",
                "request_id": request_id
            }), 400
        
        # Validate parameter ranges
        if start < 0:
            logger.warning(f"[{request_id}] Invalid start parameter: {start}")
            return jsonify({
                "success": False,
                "error": "Invalid start parameter",
                "message": "Start parameter must be non-negative",
                "request_id": request_id
            }), 400
            
        if num_reviews <= 0 or num_reviews > 1000:
            logger.warning(f"[{request_id}] Invalid num_reviews parameter: {num_reviews}")
            return jsonify({
                "success": False,
                "error": "Invalid num_reviews parameter",
                "message": "Number of reviews must be between 1 and 1000",
                "request_id": request_id
            }), 400
        
        # Import services with error handling
        try:
            from services.data_processor import DataProcessor
            from services.sentiment_analyzer import SentimentAnalyzer
        except ImportError as e:
            logger.error(f"[{request_id}] Failed to import services: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Service unavailable",
                "message": "Sentiment analysis service is not available",
                "request_id": request_id
            }), 503
        
        # Fetch raw review data
        try:
            with SerpAPIClient() as client:
                logger.info(f"[{request_id}] Fetching review data for sentiment analysis")
                review_data = client.fetch_reviews(start=start, num_reviews=num_reviews)
        except SerpAPIError as e:
            logger.error(f"[{request_id}] SerpAPI error: {str(e)}")
            return jsonify({
                "success": False,
                "error": "Data retrieval error",
                "message": "Unable to fetch review data for sentiment analysis",
                "request_id": request_id
            }), 503
        
        # Process the data with error handling
        try:
            processor = DataProcessor()
            transformed_reviews = processor.transform_review_data(review_data.get('reviews', []))
            
            if not transformed_reviews:
                logger.info(f"[{request_id}] No reviews available for sentiment analysis")
                return jsonify({
                    "success": True,
                    "data": {
                        "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
                        "sentiment_percentages": {"positive": 0.0, "negative": 0.0, "neutral": 0.0},
                        "total_reviews": 0,
                        "analyzed_reviews": 0,
                        "average_confidence": 0.0
                    },
                    "message": "No reviews available for sentiment analysis",
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            logger.info(f"[{request_id}] Analyzing sentiment for {len(transformed_reviews)} reviews")
            
            # Analyze sentiment with error handling
            try:
                analyzer = SentimentAnalyzer()
                sentiment_results = analyzer.analyze_batch(transformed_reviews)
                
                # Validate sentiment results
                if not sentiment_results or not isinstance(sentiment_results, dict):
                    logger.error(f"[{request_id}] Invalid sentiment analysis results")
                    return jsonify({
                        "success": False,
                        "error": "Analysis error",
                        "message": "Sentiment analysis produced invalid results",
                        "request_id": request_id
                    }), 500
                
                # Ensure required fields are present
                required_fields = ['sentiment_distribution', 'sentiment_percentages', 'total_reviews']
                missing_fields = [field for field in required_fields if field not in sentiment_results]
                
                if missing_fields:
                    logger.error(f"[{request_id}] Missing required fields in sentiment results: {missing_fields}")
                    return jsonify({
                        "success": False,
                        "error": "Analysis error",
                        "message": "Sentiment analysis results are incomplete",
                        "request_id": request_id
                    }), 500
                
                logger.info(f"[{request_id}] Successfully analyzed sentiment")
                
                return jsonify({
                    "success": True,
                    "data": sentiment_results,
                    "metadata": review_data.get('metadata', {}),
                    "request_id": request_id,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            except Exception as e:
                logger.error(f"[{request_id}] Error during sentiment analysis: {str(e)}", exc_info=True)
                return jsonify({
                    "success": False,
                    "error": "Sentiment analysis error",
                    "message": "Unable to analyze sentiment of review data",
                    "request_id": request_id
                }), 500
                
        except Exception as e:
            logger.error(f"[{request_id}] Error processing review data: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": "Data processing error",
                "message": "Unable to process review data for sentiment analysis",
                "request_id": request_id
            }), 500
        
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error in get_sentiment: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred while analyzing sentiment",
            "request_id": request_id
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring and debugging"""
    try:
        # Check system status
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "services": {}
        }
        
        # Check environment configuration
        health_status["services"]["configuration"] = {
            "status": "ok" if os.getenv('SERPAPI_KEY') and os.getenv('PLACE_ID') else "degraded",
            "has_api_key": bool(os.getenv('SERPAPI_KEY')),
            "has_place_id": bool(os.getenv('PLACE_ID'))
        }
        
        # Test SerpAPI connectivity (quick test)
        try:
            if os.getenv('SERPAPI_KEY') and os.getenv('PLACE_ID'):
                with SerpAPIClient() as client:
                    # Just test client initialization, don't make actual API call
                    health_status["services"]["serpapi"] = {"status": "ok", "message": "Client initialized"}
            else:
                health_status["services"]["serpapi"] = {"status": "not_configured", "message": "Missing configuration"}
        except Exception as e:
            health_status["services"]["serpapi"] = {"status": "error", "message": str(e)}
        
        # Check if any services are degraded
        overall_status = "healthy"
        for service_name, service_status in health_status["services"].items():
            if service_status["status"] in ["degraded", "error", "not_configured"]:
                overall_status = "degraded"
                break
        
        health_status["status"] = overall_status
        
        status_code = 200 if overall_status == "healthy" else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Health check failed",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Restaurant Review Dashboard server...")
    logger.info(f"Configuration check - API Key: {'✓' if os.getenv('SERPAPI_KEY') else '✗'}, Place ID: {'✓' if os.getenv('PLACE_ID') else '✗'}")
    
    try:
        # Use PORT environment variable for cloud deployment, fallback to 8000 for local
        port = int(os.environ.get('PORT', 8000))
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)