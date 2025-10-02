# Documentation System - User Guide

## Overview
The hybrid documentation system allows you to manage project documentation with both file uploads (PDFs, images) and embedded Google Docs/Slides/Sheets.

## Adding Documents

### Via Django Admin
1. Go to `/admin/users/document/add/`
2. Fill in the document details:
   - **Title**: Name of the document
   - **Description**: Brief description (optional)
   - **Category**: Select the appropriate category
   - **Doc Type**: PDF, Google Doc, Google Slides, etc.
   - **Order**: Display order within category (lower numbers appear first)

### For PDF/Image Files
1. Upload the file using the "File" field
2. Click "Save"

### For Google Docs/Slides/Sheets
1. Open your Google Doc/Slides/Sheets
2. Click "Share" → "Get link"
3. Make sure it's set to "Anyone with the link can view"
4. Copy the full URL (e.g., `https://docs.google.com/document/d/YOUR_DOC_ID/edit`)
5. Paste it in the "Google doc url" field
6. The "Embed url" will be auto-generated
7. Click "Save"

## Document Categories

- **Requirements & Analysis**: Requirements specifications, use cases, user stories
- **Design & Architecture**: System architecture, database schemas, wireframes
- **Implementation**: Code documentation, development notes
- **Testing & Quality Assurance**: Test plans, test results, bug reports
- **User Guide & Documentation**: User manuals, how-to guides
- **Presentations**: Project presentations, demos
- **Other**: Miscellaneous documents

## Viewing Documents

### Users can:
- Browse documents by category
- View embedded Google Docs directly on the page
- Download PDF files
- Open Google Docs in a new tab
- See view counts for each document

## Tips for Best Results

### Google Docs Sharing
- Always set to "Anyone with the link can view"
- Use the full sharing URL (not shortened links)
- Wait a moment after sharing before adding to the system

### File Uploads
- PDFs work best for formal documents
- Images are great for screenshots and diagrams
- Keep file sizes reasonable (< 10MB recommended)

### Organization
- Use the "Order" field to control display sequence
- Group related documents in the same category
- Use clear, descriptive titles

## URL Format Examples

**Google Docs:**
```
https://docs.google.com/document/d/1ABC123XYZ/edit
```

**Google Slides:**
```
https://docs.google.com/presentation/d/1ABC123XYZ/edit
```

**Google Sheets:**
```
https://docs.google.com/spreadsheets/d/1ABC123XYZ/edit
```

## Troubleshooting

### Google Doc not displaying?
1. Check that the document is set to "Anyone with the link can view"
2. Verify the URL is correct
3. Try regenerating the embed URL by editing and saving the document

### File not uploading?
1. Check file size (Cloudinary free tier has limits)
2. Verify file type is supported
3. Check internet connection

## View Tracking
- Each document tracks how many times it's been viewed
- Useful for understanding which documents are most accessed
- View count increments when someone clicks "View Document"
