# React Frontend - Ontology-Guided Semantic Storage

Clean, academic-style UI for schema mapping, semantic queries, and compression.

## Features

### 1. Schema Mapping View
- Upload database schema fields (table, field name, data type)
- Get GNN predictions for ontology property mappings
- View confidence scores for each prediction
- See ontology property details

### 2. Semantic Query View
- Select from pre-defined query templates (research-safe)
- View generated SQL
- Execute queries with parameters
- Display results in tables

### 3. Compression View
- Input JSON records for compression
- Visualize 4-layer compression
- See before/after metrics
- View compression layers and their contributions

## Tech Stack

- **React 18** - UI framework (functional components + hooks)
- **Vite** - Build tool (fast, modern)
- **Axios** - HTTP client for API calls
- **Recharts** - Simple charts for metrics visualization
- **CSS** - Minimal, clean styling (no heavy frameworks)

## Installation

```bash
cd frontend

# Install dependencies
npm install
```

## Running

### Development Mode

```bash
# Start development server (http://localhost:3000)
npm run dev
```

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## API Integration

The frontend communicates with the FastAPI backend running on `http://localhost:8000`.

**Proxy configuration** (in `vite.config.js`):
- `/api/*` → `http://localhost:8000/*`

### API Endpoints Used

1. **Schema Mapping:**
   - `POST /schema/predict` - Predict ontology mappings

2. **Semantic Queries:**
   - `GET /query/templates` - Get query templates
   - `POST /query/execute` - Execute query

3. **Compression:**
   - `POST /compression/evaluate` - Evaluate compression

## Project Structure

```
frontend/
├── package.json          # Dependencies
├── vite.config.js        # Vite configuration
├── index.html            # HTML template
├── src/
│   ├── main.jsx          # Entry point
│   ├── App.jsx           # Main app with navigation
│   ├── index.css         # Global styles
│   └── views/
│       ├── SchemaMapping.jsx    # Schema mapping view
│       ├── SemanticQuery.jsx    # Query view
│       └── Compression.jsx      # Compression view
```

## Running Full System

### Start Backend (Terminal 1)

```bash
# From project root
cd api
pip install fastapi uvicorn
python main.py
```

Backend runs on: `http://localhost:8000`

### Start Frontend (Terminal 2)

```bash
# From project root
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:3000`

### Access

Open browser: `http://localhost:3000`

## Design Principles

- **Clean & Academic:** Minimal design, no flashy animations
- **Functional:** All features work without gimmicks
- **Responsive:** Works on desktop and tablet
- **Accessible:** Good contrast, clear labels
- **Fast:** Vite build, minimal dependencies

## Screenshots

### Schema Mapping
- Add database fields
- View predictions with confidence scores
- See ontology property details

### Semantic Queries
- Select query templates
- View generated SQL
- Execute with parameters
- Display results

### Compression
- Input JSON records
- View compression metrics (48%+ reduction)
- Visualize before/after with charts
- See compression layers

## Development Notes

### Adding New Views

1. Create component in `src/views/`
2. Import in `App.jsx`
3. Add navigation tab
4. Connect to API endpoints

### Styling

Uses simple class-based CSS (no Tailwind, no styled-components):
- `.card` - Content containers
- `.button` - Buttons
- `.input`, `.select`, `.textarea` - Form elements
- `.badge` - Status badges
- `.tab-nav` - Navigation

### API Integration

Example API call:

```javascript
import axios from 'axios'

const response = await axios.post('/api/compression/evaluate', {
  records: [...],
  ontology_class: 'Customer'
})
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Production Deployment

```bash
# Build
npm run build

# Serve with any static server
npx serve -s dist

# Or deploy to:
# - Vercel
# - Netlify
# - GitHub Pages
# - AWS S3 + CloudFront
```

## License

MIT License - Research/College Project 2026
