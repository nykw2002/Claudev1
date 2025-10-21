# Document Processing Frontend

Next.js frontend application for document processing with AI.

## Features

- Drag-and-drop PDF file upload
- Multi-file support
- Real-time processing status
- AI-powered document analysis results
- Quality metrics visualization
- Responsive design with Tailwind CSS
- TypeScript for type safety

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment

Create or edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx           # Main application page
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/
│   ├── FileUpload.tsx     # File upload component
│   ├── PromptInput.tsx    # Prompt input component
│   ├── ProcessingStatus.tsx  # Status indicator
│   └── ResultsDisplay.tsx # Results visualization
├── services/
│   └── api.ts             # Backend API client
├── types/
│   └── index.ts           # TypeScript interfaces
├── public/                # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Components

### FileUpload
- Drag-and-drop interface
- Multiple file selection
- PDF validation
- File list with remove functionality
- File size display

### PromptInput
- Text area for user questions
- Character count (max 1000)
- Placeholder examples
- Disabled state during processing

### ProcessingStatus
- Visual status indicators
- Loading animations
- Progress feedback
- Error states

### ResultsDisplay
- Final answer display
- Quality metrics visualization
- Confidence and accuracy scores
- Document sections referenced
- Collapsible agent outputs
- Processing time

## Usage Flow

1. **Upload Files**: Drag-and-drop or click to upload PDF files
2. **Enter Prompt**: Type your question about the documents
3. **Submit**: Click "Process Documents" button
4. **View Status**: See real-time upload and processing status
5. **Review Results**: View final answer with quality metrics

## API Integration

The frontend communicates with the backend API:

- `POST /api/upload` - Upload PDF files
- `POST /api/process` - Process documents with AI
- `GET /api/health` - Health check
- `DELETE /api/upload/cleanup` - Clean up temp files

## Styling

- **Tailwind CSS** for utility-first styling
- **Lucide React** for icons
- **Custom theme** with primary color palette
- **Responsive design** for mobile and desktop

## TypeScript Types

All API responses and data structures are fully typed:

- `RuntimeJSON` - Request payload
- `AIResponse` - Processing result
- `Metrics` - Quality metrics
- `SectionUsed` - Document sections
- `ProcessingStatus` - Status states

## Development Tips

- Hot reload enabled for fast development
- TypeScript errors shown in real-time
- Console logs for debugging API calls
- Error boundaries for graceful error handling

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Code splitting with Next.js
- Optimized images and assets
- Lazy loading for components
- Efficient re-renders with React hooks
