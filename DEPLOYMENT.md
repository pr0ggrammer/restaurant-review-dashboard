# Restaurant Review Dashboard - Deployment Guide

## 🚀 Quick Deployment Options

### 1. Railway Deployment (Recommended)

Railway is the easiest option with automatic builds and deployments.

#### Prerequisites
- Node.js installed
- Git repository

#### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Deploy**
   ```bash
   # Initialize Railway project
   railway link
   
   # Deploy the application
   railway up
   ```

4. **Set Environment Variables**
   Go to your Railway dashboard and add:
   - `SERPAPI_KEY`: `21fb6a53e8611b38fa10664a012d46729f86e7a31bdd6b54e15b99fa89ca0bc5`
   - `PLACE_ID`: `central-park-boathouse-new-york-2`

5. **Access Your App**
   Railway will provide a URL like: `https://your-app-name.railway.app`

---

### 2. Vercel Deployment

Vercel is great for serverless deployment with automatic scaling.

#### Prerequisites
- Vercel account
- Git repository

#### Steps:

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   # Deploy from current directory
   vercel
   
   # Follow the prompts:
   # - Set up and deploy? Yes
   # - Which scope? (select your account)
   # - Link to existing project? No
   # - Project name? restaurant-review-dashboard
   # - Directory? ./
   # - Override settings? No
   ```

4. **Environment Variables**
   The environment variables are already configured in `vercel.json`, but you can also set them via:
   ```bash
   vercel env add SERPAPI_KEY
   vercel env add PLACE_ID
   ```

5. **Access Your App**
   Vercel will provide a URL like: `https://restaurant-review-dashboard.vercel.app`

---

## 🔧 Configuration Files

### Railway Configuration (`railway.json`)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Vercel Configuration (`vercel.json`)
```json
{
  "version": 2,
  "builds": [
    {
      "src": "vercel_app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "vercel_app.py"
    }
  ]
}
```

---

## 🌐 Environment Variables

Both platforms need these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `SERPAPI_KEY` | `21fb6a53e8611b38fa10664a012d46729f86e7a31bdd6b54e15b99fa89ca0bc5` | SerpAPI authentication key |
| `PLACE_ID` | `central-park-boathouse-new-york-2` | OpenTable restaurant identifier |

---

## 🔍 Troubleshooting

### Common Issues:

1. **Build Failures**
   - Ensure `requirements.txt` is in the root directory
   - Check Python version compatibility

2. **Environment Variables Not Set**
   - Verify variables are set in the platform dashboard
   - Check variable names match exactly

3. **API Authentication Errors**
   - Verify SerpAPI key is valid
   - Check if the key has access to OpenTable Reviews engine

4. **Port Issues**
   - The app automatically uses the `PORT` environment variable
   - Railway and Vercel set this automatically

### Health Check Endpoints:

- **Health Check**: `/health`
- **API Status**: `/api/reviews?num=1`

### Demo Mode:

If you encounter API issues, you can deploy the demo version instead:
```bash
# For Railway
railway up --start-command "python demo_server.py"

# For Vercel, modify vercel.json to use demo_server.py
```

---

## 📊 Monitoring

Both platforms provide:
- **Logs**: Real-time application logs
- **Metrics**: Performance and usage statistics
- **Alerts**: Automatic notifications for issues

### Railway Monitoring:
- Dashboard: `https://railway.app/dashboard`
- Logs: Available in project dashboard

### Vercel Monitoring:
- Dashboard: `https://vercel.com/dashboard`
- Analytics: Built-in performance monitoring

---

## 🔄 Continuous Deployment

Both platforms support automatic deployments:

1. **Connect Git Repository**
   - Link your GitHub/GitLab repository
   - Enable automatic deployments on push

2. **Branch Configuration**
   - Production: `main` branch
   - Staging: `develop` branch (optional)

3. **Build Triggers**
   - Automatic on git push
   - Manual deployment via CLI or dashboard

---

## 💡 Tips for Success

1. **Test Locally First**
   ```bash
   python app.py
   # Visit http://localhost:8000
   ```

2. **Use Demo Mode for Testing**
   ```bash
   python demo_server.py
   # Visit http://localhost:8001
   ```

3. **Monitor Logs**
   - Check deployment logs for errors
   - Monitor application logs for runtime issues

4. **Performance Optimization**
   - Both platforms auto-scale
   - Monitor response times and adjust if needed

---

## 🆘 Support

If you encounter issues:

1. **Railway Support**: https://railway.app/help
2. **Vercel Support**: https://vercel.com/support
3. **Application Logs**: Check platform dashboards for detailed error messages