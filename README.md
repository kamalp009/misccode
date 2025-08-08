# KEDB Draft Generator App

A React application for generating KEDB (Knowledge Error Database) entries with API integration, Excel file processing, and DOCX export capabilities.

## 🚀 Quick Start

1. **Install Node.js** (if not already installed)
   - Download from: https://nodejs.org/
   - Install version 16 or higher

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Set up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your API endpoint
   ```

4. **Start Development Server**
   ```bash
   npm start
   ```

5. **Open in Browser**
   - The app will open at http://localhost:3000
   - The page will reload automatically when you make changes

## 🎯 Features

### ✅ **Working Features**
- **Working Tooltip**: Hover over the info (ℹ) icon to see help text
- **API Integration**: Real API calls to fetch KEDBs and generate content
- **Find KEDB**: Search for existing KEDB entries via API
- **Generate KEDB**: Create new KEDB content via API with loading states
- **Open KEDB**: View predefined KEDB content directly
- **Download**: Export content as DOCX file
- **Error Handling**: Graceful fallback when API is unavailable
- **Loading States**: Visual feedback during API calls
- **Responsive Design**: Works on desktop and mobile

### 🔧 **API Integration**
- **Real API Calls**: No more sample data, connects to your backend
- **Loading States**: Shows spinner and "Processing..." during API calls
- **Error Handling**: Displays error messages and provides fallback data
- **Configurable**: Environment variables for API endpoints

### 💡 **Fixed Tooltip**
- **Proper Implementation**: Uses React component with CSS animations
- **Hover & Click**: Works on both hover and click
- **Mobile Friendly**: Responsive design for touch devices
- **Professional Styling**: Smooth animations and proper positioning

## 📁 Project Structure

```
kedb-draft-generator/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/
│   │   ├── Tooltip.js          # Tooltip component
│   │   └── Tooltip.css         # Tooltip styles
│   ├── services/
│   │   └── apiService.js       # API integration
│   ├── App.js                  # Main React component
│   ├── App.css                 # Component styles
│   ├── index.js                # Entry point
│   └── index.css               # Global styles
├── .env                        # Environment variables
├── package.json                # Dependencies and scripts
└── API_DOCUMENTATION.md        # API documentation
```

## 🔧 Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## 🌐 API Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
REACT_APP_API_BASE_URL=http://localhost:3001/api
REACT_APP_API_TIMEOUT=30000
```

### Required API Endpoints

1. **POST** `/api/suggested-kedbs` - Find suggested KEDBs
2. **POST** `/api/generate-kedb` - Generate new KEDB content

See `API_DOCUMENTATION.md` for detailed API specifications.

## 📦 Dependencies

- **React 18** - UI framework
- **axios** - HTTP client for API calls
- **xlsx** - Excel file processing
- **file-saver** - File download functionality
- **docx** - Word document generation

## 🐛 Troubleshooting

### Tooltip Not Working
✅ **Fixed** - The tooltip now uses a proper React component with CSS animations

### API Issues
- Check that your API server is running
- Verify the API endpoints match the documentation
- Check browser console for error messages
- The app includes fallback data when API calls fail

### General Issues
1. **Clear npm cache**: `npm cache clean --force`
2. **Delete node_modules**: `rm -rf node_modules && npm install`
3. **Check Node.js version**: `node --version` (should be 16+)
4. **Restart development server**: Stop with Ctrl+C and run `npm start` again

## 🌐 Browser Support

Modern browsers that support ES6+ features:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 📝 Usage

1. **Enter incident description** in the input field
2. **Hover over info icon** to see tooltip with help
3. **Click "Find KEDB"** to search via API (shows loading spinner)
4. **Click "Open"** on any entry to view content in editor
5. **Edit content** as needed in the textarea
6. **Click "Download"** to export as DOCX file
7. **Use "Cancel"** to return to suggested entries
8. **Use "Generate KEDB"** to create new content via API

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

This creates a `build` folder with optimized production files.

### Environment Variables for Production
Make sure to set the production API URL in your deployment environment.

## 🆘 Support

If you need help:
1. Check the tooltip by hovering over the info icon
2. Review this README file
3. Check the API documentation in `API_DOCUMENTATION.md`
4. Look at the browser console for error messages
5. Verify your API server is running and accessible