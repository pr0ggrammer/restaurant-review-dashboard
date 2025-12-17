# 🍽️ Restaurant Review Dashboard

A modern, glass morphism-styled web application that provides comprehensive analytics and visualization of restaurant reviews from OpenTable. Built with Flask and powered by SerpAPI integration.

![Dashboard Preview](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **📊 Real-time Analytics**: Live restaurant review data from OpenTable
- **🎨 Glass Morphism UI**: Modern, translucent design with blur effects
- **📈 Interactive Charts**: Rating trends, sentiment analysis, and review volume
- **🤖 Sentiment Analysis**: AI-powered classification of review emotions
- **📱 Responsive Design**: Works perfectly on desktop and mobile
- **⚡ Fast Performance**: Optimized for speed with concurrent request handling
- **🔄 Auto-refresh**: Real-time data updates without page reload

## 🚀 Live Demo

- **Production**: [Deploy to Vercel](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/restaurant-review-dashboard)
- **Demo Mode**: Includes mock data for testing without API keys

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML5, CSS3, JavaScript, Chart.js
- **API**: SerpAPI (OpenTable Reviews)
- **Deployment**: Vercel, Railway, Heroku
- **Testing**: pytest, Hypothesis (Property-based testing)

## 📋 Requirements

- Python 3.11+
- SerpAPI account (for live data)
- Modern web browser

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/restaurant-review-dashboard.git
cd restaurant-review-dashboard
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file:
```env
SERPAPI_KEY=your_serpapi_key_here
PLACE_ID=central-park-boathouse-new-york-2
FLASK_ENV=development
```

### 5. Run the Application
```bash
# Production mode
python app.py

# Demo mode (no API key required)
python demo_server.py
```

Visit `http://localhost:8000` (production) or `http://localhost:8001` (demo)

## 🌐 Deployment

### Quick Deploy to Vercel
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/restaurant-review-dashboard)

### Manual Deployment
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for multiple platforms.

## 📊 API Endpoints

| Endpoint | Description | Parameters |
|----------|-------------|------------|
| `/` | Main dashboard | - |
| `/health` | Health check | - |
| `/api/reviews` | Raw review data | `start`, `num` |
| `/api/metrics` | Aggregated statistics | `interval`, `num` |
| `/api/sentiment` | Sentiment analysis | `num` |

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run property-based tests
python test_property_simple.py

# Run integration tests
python test_integration.py

# Run error handling tests
python test_error_handling.py
```

## 📈 Features Overview

### Dashboard Components
- **Overview Metrics**: Total reviews, average rating, sentiment score
- **Rating Trends**: Time-series visualization of rating changes
- **Review Volume**: Bar charts showing review frequency
- **Sentiment Analysis**: Pie charts of positive/negative/neutral sentiment
- **Theme Extraction**: Key topics from review content
- **Rating Distribution**: Breakdown by star ratings

### Technical Features
- **Concurrent Request Handling**: Thread-safe operations
- **Comprehensive Error Handling**: Graceful degradation
- **Property-Based Testing**: Formal correctness verification
- **Glass Morphism Design**: Modern UI with blur effects
- **Responsive Layout**: Mobile-friendly design

## 🔒 Security

- Environment variables for sensitive data
- Input validation and sanitization
- Rate limiting and error handling
- Secure API key management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/restaurant-review-dashboard/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/restaurant-review-dashboard/discussions)

## 🙏 Acknowledgments

- [SerpAPI](https://serpapi.com/) for OpenTable data access
- [Chart.js](https://www.chartjs.org/) for beautiful visualizations
- [Flask](https://flask.palletsprojects.com/) for the web framework
- Glass morphism design inspiration from modern UI trends

---

**⭐ Star this repository if you found it helpful!**