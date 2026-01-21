# User Guide for Field Officials

## Land Record Digitization Tool

A web-based application for correlating textual land records with spatial parcel boundaries and identifying discrepancies.

---

## Getting Started

### Accessing the Application

1. Open your web browser (Chrome, Firefox, or Edge recommended)
2. Navigate to the application URL provided by your administrator
3. The application will load showing the map and search panel

### Interface Overview

![Interface Layout]

The interface consists of:
- **Header** - Application title and user login
- **Search Panel** - Search by plot ID or owner name
- **Village List** - Quick access to village parcels
- **Reconciliation Summary** - Match/mismatch statistics
- **Map** - Interactive parcel visualization
- **Detail Panel** - Detailed parcel information (appears on selection)

---

## Searching for Records

### Search by Plot ID

1. Click the **"Plot ID"** tab in the search panel
2. Enter the plot ID (e.g., `RAM-001`)
3. Results appear automatically as you type
4. Click a result to view on map

### Search by Owner Name

1. Click the **"Owner Name"** tab
2. Enter the owner's name (partial matches work)
3. Results show with match scores
4. Higher scores indicate closer matches

### Tips for Effective Searching

- Use at least 2-3 characters for faster results
- Owner name search uses fuzzy matching (handles spelling variations)
- Plot ID search is case-insensitive

---

## Understanding the Map

### Color Legend

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | Match | Owner names match between spatial and textual records |
| 🟡 Yellow | Partial | Names are similar but not exact (needs review) |
| 🔴 Red | Mismatch | Significant difference in recorded names |
| 🟣 Purple | Selected | Currently selected parcel |

### Map Navigation

- **Zoom In/Out** - Use scroll wheel or +/- buttons
- **Pan** - Click and drag the map
- **Zoom to All** - Click the expand icon (↔) in top-right
- **Click Parcel** - View popup with basic info
- **Click Village** - Zoom to that village's parcels

---

## Viewing Parcel Details

When you click a parcel or search result, the detail panel shows:

### Basic Information
- Village name
- Survey number
- Area (in square meters)
- Land type

### Owner Information
- Current owner name (from textual record)
- Father's/husband's name
- Registration date

### Comparison Analysis
- Side-by-side comparison of textual vs spatial names
- Similarity score (0-100%)
- Match status indicator

---

## Using the Reconciliation Report

### Viewing the Report

1. Click **"View Full Report"** in the Reconciliation panel
2. The report shows:
   - Summary statistics
   - Priority review items (mismatches)
   - Partial matches needing verification
   - Verified matches

### Understanding the Report

- **Priority Review** - Records requiring immediate attention
- **Partial Matches** - Minor discrepancies that need verification
- **Verified Matches** - Records where names match correctly

### Exporting Data

1. Open the reconciliation report
2. Click **"Export CSV"** to download
3. File saves with current date in filename
4. Open in Excel or similar software

### Printing

1. Open the reconciliation report
2. Click **"Print Report"**
3. A print-friendly version opens in new window

---

## Editing Records (Authorized Users Only)

### Prerequisites

- Must be logged in with **editor** or **admin** role
- Only textual records can be modified

### How to Edit

1. Select a parcel on the map or through search
2. In the detail panel, click **"Edit Record"**
3. Update the fields as needed:
   - Owner Name
   - Area
   - Father's Name
   - Land Type
4. Click **"Save Changes"**
5. Map and statistics update automatically

### Edit History

All edits are logged with:
- Username of editor
- Timestamp
- Previous and new values

---

## Logging In

### For Registered Users

1. Click **"Login"** in the top-right corner
2. Enter your username and password
3. Click **"Login"**

### User Roles

| Role | Can View | Can Search | Can Edit |
|------|----------|------------|----------|
| Viewer | ✓ | ✓ | ✗ |
| Editor | ✓ | ✓ | ✓ |
| Admin | ✓ | ✓ | ✓ |

### Test Accounts (Demo Only)

| Username | Password | Role |
|----------|----------|------|
| viewer1 | viewer123 | Viewer |
| editor1 | editor123 | Editor |
| admin1 | admin123 | Admin |

---

## Common Tasks

### Task: Find a Specific Plot

1. Enter plot ID in search box
2. Click result to locate on map
3. Review details in side panel

### Task: Find Owner's Parcels

1. Switch to "Owner Name" search
2. Enter owner's name
3. All matching parcels will be listed
4. Click each to view on map

### Task: Review Mismatches for a Village

1. Click village name in the list
2. Map zooms to village area
3. Red parcels are mismatches
4. Click each to see comparison details

### Task: Generate Village Report

1. Open full reconciliation report
2. Note statistics for each village
3. Export to CSV for detailed analysis

---

## Troubleshooting

### Map Not Loading

1. Check internet connection
2. Refresh the page (F5)
3. Clear browser cache
4. Try a different browser

### Search Not Working

1. Ensure you typed at least 2 characters
2. Check spelling of plot ID format (e.g., RAM-001)
3. Try broader search terms

### Cannot Edit Records

1. Verify you are logged in
2. Confirm your account has editor access
3. Contact administrator if access needed

### Session Expired

1. You'll see "Token expired" message
2. Click Login to authenticate again
3. Your work is not lost

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Enter | Execute search |
| Esc | Close popup/modal |
| + | Zoom in |
| - | Zoom out |

---

## Getting Help

For technical support, contact your system administrator.

**Application Version:** 1.0.0

---

## Glossary

- **Plot ID** - Unique identifier for a land parcel
- **Survey Number** - Official cadastral reference number
- **Reconciliation** - Process of comparing records from different sources
- **Fuzzy Matching** - Matching names that are similar but not exact
- **GeoJSON** - Geographic data format used for parcel boundaries
