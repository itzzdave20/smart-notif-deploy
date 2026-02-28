# 🔔 Chat Ping - Smart Notification App

A comprehensive AI-powered smart notification application with attendance tracking, designed for mobile use.

## 🚀 Quick Start

### Option 1: Run Locally for Mobile Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Start the app (mobile-friendly)
python start_mobile.py
# OR
streamlit run smart-notification-app.py --server.address 0.0.0.0
```

**Access from mobile:** `http://YOUR_IP:8501`

### Option 2: Deploy to Streamlit Community Cloud (Recommended)
1. **Push this repo to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Professional UI and Quick Meet enhancements"
   git push origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **New app** and set:
   - **Repository:** `your-username/smart-notification-app`
   - **Branch:** `main`
   - **Main file path:** `smart-notification-app.py`
4. Click **Deploy**. Your app will be live at `https://your-app-name.streamlit.app`.

## 📱 Mobile Features

### ✅ Progressive Web App (PWA)
- **Installable**: Add to home screen like native app
- **Offline Support**: Basic functionality without internet
- **Push Notifications**: Real-time alerts
- **App-like Experience**: Full screen, no browser UI

### ✅ Mobile-Optimized Interface
- **Responsive Design**: Works on all screen sizes
- **Touch-Friendly**: Large buttons and touch targets
- **Camera Integration**: Direct camera access for attendance
- **QR Code Scanning**: Mobile-optimized QR handling

## 👥 User Roles & Login

- **Student** and **Instructor** log in from the main page (tabs: **Student Login** / **Instructor Login**).  
- Check **"Remember me"** to stay signed in; closing and reopening the app will log you in automatically.  
- Log out with the sidebar **Logout** button; next visit shows the login page again.

### Admin (Full Access)
- **Username:** `admin`
- **Password:** `admin123`
- **Features:** System management, user control, analytics

### Student (Mobile-First)
- **Username:** `student`
- **Password:** `student123`
- **Features:** QR attendance, notifications, reports

### Instructor (Class Management)
- **Username:** `instructor`
- **Password:** `instructor123`
- **Features:** QR generation, class management, attendance tracking

## 📱 How to Install on Mobile

### iPhone/iPad:
1. Open app in Safari
2. Tap Share → "Add to Home Screen"
3. Tap "Add"

### Android:
1. Open app in Chrome
2. Tap Menu → "Add to Home Screen"
3. Tap "Add"

### Automatic Install:
- Users will see "📱 Install App" button
- One-tap installation!

## 🎯 Key Features

### 🎓 For Students:
- **QR Code Attendance**: Scan instructor's QR code
- **Mobile Camera**: Upload photos for attendance
- **Push Notifications**: Real-time alerts
- **Class Enrollment**: Browse and join classes
- **Quick Meet**: Join video meetings

### 👨‍🏫 For Instructors:
- **QR Code Generation**: Create attendance QR codes
- **Class Management**: Manage student enrollment
- **Mobile Dashboard**: View attendance stats
- **Quick Meet**: Start video meetings
- **Student Notifications**: Send alerts

### 🛡️ For Admins:
- **Full Mobile Control**: Complete system management
- **User Management**: Add/edit users on mobile
- **Analytics**: View reports on mobile
- **System Settings**: Configure on mobile

## 🔧 Technical Details

### Built With:
- **Backend**: Python 3.8+
- **Frontend**: Streamlit (mobile-responsive)
- **Database**: SQLite
- **AI**: scikit-learn, sentiment analysis
- **Computer Vision**: OpenCV, face recognition
- **PWA**: Service Worker, Web App Manifest

### Mobile Technologies:
- **Progressive Web App (PWA)**
- **Service Worker** for offline support
- **Web App Manifest** for installation
- **Responsive Design** for all devices
- **Touch Optimization** for mobile interaction

## 📊 Deployment Options

### Deploy to Streamlit Community Cloud (recommended)

1. **Push your app to GitHub** (this repo or a fork).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **"New app"** and set:
   - **Repository:** your GitHub repo (e.g. `yourusername/smart-notification-app`)
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `smart-notification-app.py`
4. Click **"Deploy"**. The app will use the root `requirements.txt` automatically.
5. After deploy, share the generated URL (e.g. `https://yourapp.streamlit.app`).

**Stay logged in:** Users who check **"Remember me"** when logging in (Student or Instructor) will be automatically logged in when they open the app again in the same browser. Logging out clears the session and shows the login page on the next visit.

### 1. Streamlit Cloud (Free)
- Push to GitHub → Deploy on share.streamlit.io
- Automatic HTTPS, custom domain
- Perfect for mobile apps

### 2. Railway
- Connect GitHub → Auto-deploy
- Custom domain, easy scaling

### 3. Heroku
- Traditional cloud deployment
- Full control, paid plans

### 4. Local Network
- Run locally with network access
- Perfect for testing and development

## 📱 Mobile Testing

### Test on Your Phone:
1. **Find your computer's IP**: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
2. **Run with network access**: `streamlit run smart-notification-app.py --server.address 0.0.0.0`
3. **Access from mobile**: `http://YOUR_IP:8501`
4. **Test PWA features**: Install prompt, offline mode, notifications

## 🎉 Success!

Your Smart Notification App is now:
- ✅ **Mobile-Ready**: Works on all mobile devices
- ✅ **Installable**: Add to home screen like native app
- ✅ **Offline-Capable**: Basic functionality without internet
- ✅ **Cloud-Deployed**: Accessible from anywhere
- ✅ **Multi-Platform**: iOS, Android, desktop

## 📞 Support

- **Documentation**: See `SETUP_GUIDE.md` and `MOBILE_DEPLOYMENT_GUIDE.md`
- **Issues**: Check Streamlit logs and browser console
- **Mobile Testing**: Use `python start_mobile.py` for easy testing

---

**Ready to go mobile!** 🚀📱
