# Sprint 2 — Setup + File Upload (Weeks 3–4)

## Sprint Goal
Create the first fully connected version of the application where a user can upload a MusicXML file through the frontend and receive a successful response from the backend.

This sprint focuses on establishing the project architecture, frontend/backend communication, and file upload handling. At the end of the sprint, the application should demonstrate the complete upload pipeline, even though no music parsing or tablature conversion has been implemented yet.

---

# Sprint Objectives

By the end of Sprint 2, the team should have:

- A working React + TypeScript frontend
- A working Node.js + Express backend
- Frontend and backend connected through HTTP requests
- MusicXML file uploads functioning end-to-end
- Basic routing and navigation working
- Shared development setup documented for all teammates
- Initial deployment or local run instructions available

---

# Deliverables

## Frontend Deliverables

### React App Scaffolded
The frontend application will be initialized using:

- React
- Vite
- TypeScript

The project should include:

- Organized folder structure
- Reusable components folder
- Page routing setup
- API service utilities
- Basic styling setup

Suggested structure:

```text
client/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   ├── types/
│   ├── App.tsx
│   └── main.tsx
```

---

### Upload Page UI

A functional upload interface should allow users to:

- Select a `.xml` or `.mxl` file
- Upload using:
  - file picker
  - or drag-and-drop
- Submit the file to the backend
- Receive visual confirmation of success or failure

UI components may include:

- Upload box
- Upload button
- Loading spinner
- Success/error messages

Possible future enhancement:
- File validation feedback before upload

---

### Basic Routing

React Router should be configured with at least:

| Route | Purpose |
|---|---|
| `/upload` | Main upload page |
| `/result` | Placeholder results page |

The result page does not need functionality yet. It only confirms navigation flow is working.

---

## Backend Deliverables

### Express Server Setup

The backend should be initialized using:

- Node.js
- Express
- TypeScript

The server should include:

- Organized routes
- Middleware support
- Error handling structure
- Environment variable support

Suggested structure:

```text
server/
├── src/
│   ├── routes/
│   ├── controllers/
│   ├── middleware/
│   ├── services/
│   ├── app.ts
│   └── server.ts
```

---

### Health Check Endpoint

A simple route should verify that the backend is running correctly.

Example:

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok"
}
```

This endpoint helps:
- frontend/backend testing
- deployment debugging
- verifying server availability

---

### File Upload Endpoint

The backend should accept MusicXML uploads.

Example route:

```http
POST /api/upload
```

Requirements:

- Accept `.xml` and `.mxl` files
- Store temporarily in memory or uploads folder
- Return JSON success response
- Reject unsupported file types

Example success response:

```json
{
  "success": true,
  "filename": "example.musicxml"
}
```

Example error response:

```json
{
  "success": false,
  "message": "Unsupported file type"
}
```

Suggested middleware:
- multer

---

# Integration Deliverables

## Frontend ↔ Backend Communication

The frontend should successfully:

1. Send uploaded file to backend
2. Receive backend response
3. Display upload result to user

This validates:
- API communication
- CORS configuration
- request handling
- response handling

---

## Shared Development Environment

All five teammates should be able to:

- clone the repository
- install dependencies
- run frontend and backend locally
- test file upload functionality

The team should standardize:

- Node version
- package manager
- environment variable format
- startup commands

---

# Documentation Deliverables

## README Requirements

The README should include:

### Project Overview
Short description of the application and sprint progress.

### Setup Instructions

Frontend:

```bash
cd client
npm install
npm run dev
```

Backend:

```bash
cd server
npm install
npm run dev
```

### Environment Variables

Example:

```env
PORT=5000
```

### How to Test Uploads

- Open upload page
- Select MusicXML file
- Upload file
- Verify success response

### Team Workflow

Document:
- branching strategy
- pull request expectations
- commit naming conventions

Example:

```text
feature/upload-ui
feature/backend-upload
bugfix/upload-validation
```

---

# Suggested Technologies

| Purpose | Technology |
|---|---|
| Frontend Framework | React |
| Frontend Build Tool | Vite |
| Frontend Language | TypeScript |
| Backend Runtime | Node.js |
| Backend Framework | Express |
| File Upload Handling | multer |
| HTTP Requests | Axios or Fetch API |
| Routing | React Router |
| Version Control | Git + GitHub |

---

# Team Responsibilities

| Team Member | Responsibilities |
|---|---|
| Hunter | Sprint coordination, GitHub repo management, integration |
| Rhino | Upload UI, routing, frontend styling |
| Luke & Hunter | Express server, upload endpoint, API setup |
| My Boi Jo | Research MusicXML file structure for future sprint |
| Emily | README documentation, upload testing, invalid file testing |

---

# Testing Requirements

The team should test:

## Valid Uploads
- `.xml` files
- `.mxl` files

## Invalid Uploads
- `.pdf`
- `.jpg`
- empty uploads

## Error Handling
- backend offline
- oversized files
- invalid MIME types

## UI Behavior
- upload button states
- loading indicators
- success messages
- error messages

---

# Acceptance Criteria

Sprint 2 is complete when:

- Frontend and backend both run successfully
- User can upload a MusicXML file
- Backend receives and validates the file
- Frontend displays upload success/failure
- Routes are functioning
- README allows all teammates to run the project
- Code is merged into the main development branch

---

# Out of Scope

The following features are intentionally excluded from Sprint 2:

- Parsing MusicXML contents
- Guitar tab conversion
- Note extraction
- Pitch mapping
- Rendering tablature
- PDF/image recognition
- OCR or AI transcription
- Downloadable tab generation

These features will be implemented in later sprints.

---

# Sprint Outcome

At the end of Sprint 2, the project should demonstrate a complete upload workflow and provide the technical foundation for future parsing and conversion features.

The application should feel like a real working web app, even though the musical conversion functionality has not yet been implemented.
