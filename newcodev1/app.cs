.kedb-app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
  min-height: 100vh;
}

/* Header */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.header h1 {
  font-size: 28px;
  color: #333;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.version-info {
  display: flex;
  align-items: center;
  background: #f8f9fa;
  padding: 8px 12px;
  border-radius: 20px;
  border: 1px solid #e9ecef;
}

.version-text {
  font-size: 14px;
  color: #666;
  margin-right: 5px;
}

.version-link {
  background: #007acc;
  color: white;
  border: none;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.version-link:hover {
  background: #005fa3;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,122,204,0.3);
}

.info-icon {
  width: 24px;
  height: 24px;
  background-color: #007acc;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.info-icon:hover {
  background-color: #005fa3;
  transform: scale(1.1);
}

/* Input Section */
.input-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.input-section label {
  display: block;
  margin-bottom: 10px;
  font-weight: 600;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  margin-bottom: 15px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0,122,204,0.2);
}

.form-control:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

/* Buttons */
.button-group {
  display: flex;
  gap: 15px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  position: relative;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #007acc;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #005fa3;
}

.btn-secondary {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ddd;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #218838;
}

.btn-open {
  background-color: #6c757d;
  color: white;
  padding: 6px 16px;
  font-size: 12px;
}

.btn-open:hover {
  background-color: #5a6268;
}

/* Loading */
.loading-section {
  background: white;
  padding: 40px 20px;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007acc;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-section p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* Suggested KEDBs */
.suggested-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.suggested-section h2 {
  margin: 0 0 20px 0;
  font-size: 22px;
  color: #333;
}

.kedb-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.kedb-item {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 15px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.kedb-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.kedb-header {
  margin-bottom: 10px;
  line-height: 1.5;
}

.kedb-number {
  font-weight: bold;
  color: #666;
}

.kedb-id {
  font-weight: bold;
  color: #007acc;
  margin-left: 5px;
}

.kedb-title {
  margin-left: 5px;
  color: #333;
}

.recommended-badge {
  background-color: #28a745;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 10px;
}

/* Editor */
.editor-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.editor-header h3 {
  margin: 0 0 15px 0;
  font-size: 18px;
  color: #333;
}

.editor-textarea {
  width: 100%;
  min-height: 400px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  box-sizing: border-box;
  background: #fafafa;
  transition: border-color 0.3s ease;
}

.editor-textarea:focus {
  outline: none;
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0,122,204,0.2);
}

.editor-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .kedb-app {
    padding: 10px;
  }
  
  .header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-right {
    justify-content: center;
  }
  
  .button-group {
    flex-direction: column;
  }
  
  .editor-actions {
    flex-direction: column;
    gap: 10px;
  }
}
