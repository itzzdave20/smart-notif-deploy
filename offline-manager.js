// Offline Data Manager for Chat Ping
// Handles offline storage, sync, and online/offline status

class OfflineManager {
  constructor() {
    this.isOnline = navigator.onLine;
    this.syncQueue = [];
    this.offlineData = new Map();
    this.syncInProgress = false;
    
    this.init();
  }
  
  init() {
    // Listen for online/offline events
    window.addEventListener('online', () => this.handleOnline());
    window.addEventListener('offline', () => this.handleOffline());
    
    // Set up periodic sync
    this.setupPeriodicSync();
    
    // Initialize offline storage
    this.initOfflineStorage();
    
    // Show initial status
    this.updateOnlineStatus();
  }
  
  // Online/Offline event handlers
  handleOnline() {
    console.log('OfflineManager: Back online!');
    this.isOnline = true;
    this.updateOnlineStatus();
    this.syncOfflineData();
  }
  
  handleOffline() {
    console.log('OfflineManager: Gone offline');
    this.isOnline = false;
    this.updateOnlineStatus();
  }
  
  // Update UI to show online/offline status
  updateOnlineStatus() {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
      statusElement.textContent = this.isOnline ? '🟢 Online' : '🔴 Offline';
      statusElement.className = this.isOnline ? 'online' : 'offline';
    }
    
    // Show/hide offline indicators
    const offlineIndicators = document.querySelectorAll('.offline-indicator');
    offlineIndicators.forEach(indicator => {
      indicator.style.display = this.isOnline ? 'none' : 'block';
    });
    
    // Show/hide sync buttons
    const syncButtons = document.querySelectorAll('.sync-button');
    syncButtons.forEach(button => {
      button.style.display = this.isOnline ? 'none' : 'inline-block';
    });
  }
  
  // Initialize offline storage (IndexedDB)
  async initOfflineStorage() {
    try {
      // Check if IndexedDB is available
      if ('indexedDB' in window) {
        this.db = await this.openDatabase();
        console.log('OfflineManager: IndexedDB initialized');
      } else {
        console.log('OfflineManager: IndexedDB not available, using localStorage');
        this.useLocalStorage = true;
      }
    } catch (error) {
      console.log('OfflineManager: Storage initialization failed', error);
      this.useLocalStorage = true;
    }
  }
  
  // Open IndexedDB database
  openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open('ChatPingOffline', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores for different data types
        if (!db.objectStoreNames.contains('attendance')) {
          db.createObjectStore('attendance', { keyPath: 'id', autoIncrement: true });
        }
        
        if (!db.objectStoreNames.contains('notifications')) {
          db.createObjectStore('notifications', { keyPath: 'id', autoIncrement: true });
        }
        
        if (!db.objectStoreNames.contains('userData')) {
          db.createObjectStore('userData', { keyPath: 'id', autoIncrement: true });
        }
        
        if (!db.objectStoreNames.contains('syncQueue')) {
          db.createObjectStore('syncQueue', { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }
  
  // Store data offline
  async storeOfflineData(type, data) {
    try {
      if (this.useLocalStorage) {
        const key = `offline_${type}_${Date.now()}`;
        localStorage.setItem(key, JSON.stringify(data));
        return key;
      } else {
        const transaction = this.db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        const request = store.add({
          ...data,
          timestamp: Date.now(),
          synced: false
        });
        
        return new Promise((resolve, reject) => {
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
      }
    } catch (error) {
      console.log('OfflineManager: Failed to store offline data', error);
      throw error;
    }
  }
  
  // Get offline data
  async getOfflineData(type) {
    try {
      if (this.useLocalStorage) {
        const keys = Object.keys(localStorage).filter(key => key.startsWith(`offline_${type}_`));
        return keys.map(key => JSON.parse(localStorage.getItem(key)));
      } else {
        const transaction = this.db.transaction([type], 'readonly');
        const store = transaction.objectStore(type);
        const request = store.getAll();
        
        return new Promise((resolve, reject) => {
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
      }
    } catch (error) {
      console.log('OfflineManager: Failed to get offline data', error);
      return [];
    }
  }
  
  // Add to sync queue
  async addToSyncQueue(type, data) {
    const syncItem = {
      type,
      data,
      timestamp: Date.now(),
      retries: 0
    };
    
    try {
      if (this.useLocalStorage) {
        const key = `sync_queue_${Date.now()}`;
        localStorage.setItem(key, JSON.stringify(syncItem));
      } else {
        const transaction = this.db.transaction(['syncQueue'], 'readwrite');
        const store = transaction.objectStore('syncQueue');
        await store.add(syncItem);
      }
      
      this.syncQueue.push(syncItem);
      
      // Try to sync immediately if online
      if (this.isOnline) {
        this.syncOfflineData();
      }
    } catch (error) {
      console.log('OfflineManager: Failed to add to sync queue', error);
    }
  }
  
  // Sync offline data when online
  async syncOfflineData() {
    if (!this.isOnline || this.syncInProgress) {
      return;
    }
    
    this.syncInProgress = true;
    console.log('OfflineManager: Starting sync...');
    
    try {
      // Get all unsynced data
      const attendanceData = await this.getOfflineData('attendance');
      const notificationData = await this.getOfflineData('notifications');
      const userData = await this.getOfflineData('userData');
      
      // Sync each type
      await Promise.all([
        this.syncAttendanceData(attendanceData),
        this.syncNotificationData(notificationData),
        this.syncUserData(userData)
      ]);
      
      console.log('OfflineManager: Sync completed successfully');
      this.showSyncSuccess();
      
    } catch (error) {
      console.log('OfflineManager: Sync failed', error);
      this.showSyncError();
    } finally {
      this.syncInProgress = false;
    }
  }
  
  // Sync attendance data
  async syncAttendanceData(data) {
    for (const item of data) {
      if (!item.synced) {
        try {
          const response = await fetch('/api/attendance/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });
          
          if (response.ok) {
            await this.markAsSynced('attendance', item.id);
          }
        } catch (error) {
          console.log('OfflineManager: Failed to sync attendance item', error);
        }
      }
    }
  }
  
  // Sync notification data
  async syncNotificationData(data) {
    for (const item of data) {
      if (!item.synced) {
        try {
          const response = await fetch('/api/notifications/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });
          
          if (response.ok) {
            await this.markAsSynced('notifications', item.id);
          }
        } catch (error) {
          console.log('OfflineManager: Failed to sync notification item', error);
        }
      }
    }
  }
  
  // Sync user data
  async syncUserData(data) {
    for (const item of data) {
      if (!item.synced) {
        try {
          const response = await fetch('/api/user/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });
          
          if (response.ok) {
            await this.markAsSynced('userData', item.id);
          }
        } catch (error) {
          console.log('OfflineManager: Failed to sync user data item', error);
        }
      }
    }
  }
  
  // Mark data as synced
  async markAsSynced(type, id) {
    try {
      if (this.useLocalStorage) {
        // Remove from localStorage
        const keys = Object.keys(localStorage).filter(key => key.startsWith(`offline_${type}_`));
        keys.forEach(key => {
          const data = JSON.parse(localStorage.getItem(key));
          if (data.id === id) {
            localStorage.removeItem(key);
          }
        });
      } else {
        const transaction = this.db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        await store.delete(id);
      }
    } catch (error) {
      console.log('OfflineManager: Failed to mark as synced', error);
    }
  }
  
  // Setup periodic sync
  setupPeriodicSync() {
    // Sync every 30 seconds when online
    setInterval(() => {
      if (this.isOnline && !this.syncInProgress) {
        this.syncOfflineData();
      }
    }, 30000);
    
    // Check for pending syncs every 5 minutes
    setInterval(() => {
      if (this.isOnline) {
        this.checkPendingSyncs();
      }
    }, 300000);
  }
  
  // Check for pending syncs
  async checkPendingSyncs() {
    try {
      const pendingData = await this.getOfflineData('syncQueue');
      if (pendingData.length > 0) {
        console.log('OfflineManager: Found pending syncs', pendingData.length);
        this.syncOfflineData();
      }
    } catch (error) {
      console.log('OfflineManager: Failed to check pending syncs', error);
    }
  }
  
  // Show sync success message
  showSyncSuccess() {
    this.showNotification('✅ Data synced successfully!', 'success');
  }
  
  // Show sync error message
  showSyncError() {
    this.showNotification('❌ Sync failed. Will retry when online.', 'error');
  }
  
  // Show notification
  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `sync-notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#F44336' : '#2196F3'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      z-index: 10000;
      font-size: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.remove();
    }, 3000);
  }
  
  // Manual sync trigger
  async manualSync() {
    if (this.isOnline) {
      await this.syncOfflineData();
    } else {
      this.showNotification('🔴 You are offline. Data will sync when online.', 'error');
    }
  }
  
  // Get offline status
  getOfflineStatus() {
    return {
      isOnline: this.isOnline,
      syncInProgress: this.syncInProgress,
      pendingSyncs: this.syncQueue.length
    };
  }
}

// Initialize offline manager when page loads
let offlineManager;
document.addEventListener('DOMContentLoaded', () => {
  offlineManager = new OfflineManager();
  
  // Make it globally available
  window.offlineManager = offlineManager;
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = OfflineManager;
}

