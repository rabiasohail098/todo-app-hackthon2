# Todo App - Frontend

Modern task management web application built with Next.js 16, Better Auth, and Tailwind CSS.

## Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript 5.x
- **Authentication**: Better Auth 1.4+ (JWT)
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **HTTP Client**: Fetch API with custom wrapper

## Features

- ✅ User authentication (sign-up, sign-in, logout)
- ✅ JWT-based sessions with httpOnly cookies
- ✅ Protected routes with middleware
- ✅ Task CRUD operations with optimistic UI updates
- ✅ Inline task editing
- ✅ Task completion toggling
- ✅ Responsive design (mobile, tablet, desktop)
- ✅ Dark mode support
- ✅ Form validation with error handling
- ✅ Loading states

## Setup

### Prerequisites

- Node.js 18+ or Bun
- npm, yarn, pnpm, or bun
- Backend API running (see `backend/README.md`)

### Installation

1. **Install dependencies**:

   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   # or
   bun install
   ```

2. **Configure environment variables**:

   Create a `.env.local` file in the `frontend/` directory:

   ```bash
   cp .env.local.example .env.local
   ```

   Edit `.env.local` with your actual values:

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   BETTER_AUTH_SECRET=your-super-secret-32-character-key-here
   NEXT_PUBLIC_BASE_URL=http://localhost:3000
   ```

   **Important**:
   - `NEXT_PUBLIC_API_URL`: Backend API URL (must match backend CORS_ORIGINS)
   - `BETTER_AUTH_SECRET`: Same secret as backend JWT_SECRET (generate with `openssl rand -hex 32`)
   - `NEXT_PUBLIC_BASE_URL`: Frontend URL (for Better Auth callbacks)

## Running the App

### Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm run start
```

### Linting

```bash
npm run lint
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── page.tsx           # Landing page
│   ├── layout.tsx         # Root layout
│   ├── globals.css        # Global styles
│   ├── auth/              # Authentication pages
│   │   ├── sign-in/
│   │   │   └── page.tsx   # Sign-in page
│   │   └── sign-up/
│   │       └── page.tsx   # Sign-up page
│   └── dashboard/
│       └── page.tsx       # Dashboard (protected)
├── components/            # React components
│   ├── TaskForm.tsx      # Task creation form
│   ├── TaskList.tsx      # Task list with grouping
│   └── TaskItem.tsx      # Individual task item
├── lib/                  # Utilities
│   ├── api.ts           # API client wrapper
│   └── auth.ts          # Better Auth configuration
├── types/
│   └── index.ts         # TypeScript interfaces
├── middleware.ts        # Route protection
├── .env.local.example   # Environment template
├── package.json
├── next.config.ts
├── tailwind.config.ts
├── postcss.config.mjs
└── README.md
```

## Routes

| Route | Description | Protected |
|-------|-------------|-----------|
| `/` | Landing page | No |
| `/auth/sign-up` | User registration | No |
| `/auth/sign-in` | User login | No |
| `/dashboard` | Task management | Yes |

## Components

### TaskForm

Task creation form with validation:
- Title (required, max 200 chars)
- Description (optional)
- Client-side validation
- Loading states

### TaskList

Displays tasks grouped by status:
- Active tasks
- Completed tasks
- Empty state handling

### TaskItem

Individual task component with:
- Completion checkbox
- Inline editing
- Delete with confirmation
- Strikethrough for completed tasks

## API Integration

The app communicates with the backend API using the custom `apiClient` wrapper from `lib/api.ts`:

```typescript
import { apiClient } from "@/lib/api";

// GET request
const tasks = await apiClient.get<Task[]>("/api/tasks");

// POST request
const newTask = await apiClient.post<Task>("/api/tasks", {
  title: "Buy groceries",
  description: "Milk, eggs, bread"
});

// PATCH request
const updated = await apiClient.patch<Task>(`/api/tasks/${id}`, {
  is_completed: true
});

// DELETE request
await apiClient.delete(`/api/tasks/${id}`);
```

## Authentication Flow

1. **Sign Up**: User registers with email/password → JWT issued → Redirect to dashboard
2. **Sign In**: User authenticates → JWT stored in httpOnly cookie → Redirect to dashboard
3. **Protected Routes**: Middleware checks for JWT → Redirects to sign-in if missing
4. **API Calls**: JWT automatically attached to Authorization header
5. **Logout**: JWT cleared → Redirect to landing page

## Styling

### Tailwind CSS 4

Using Tailwind CSS v4 with PostCSS:

```css
/* app/globals.css */
@import "tailwindcss";
```

### Color Scheme

- **Primary**: Blue (bg-blue-600, text-blue-600)
- **Background**: Zinc (bg-zinc-100 light, bg-zinc-950 dark)
- **Text**: Zinc (text-zinc-900 light, text-zinc-50 dark)
- **Success**: Green (for completed tasks)
- **Error**: Red (for validation errors)

### Dark Mode

Automatic dark mode support using Tailwind's `dark:` modifier:

```tsx
<div className="bg-white dark:bg-zinc-900">
  <h1 className="text-zinc-900 dark:text-zinc-50">Title</h1>
</div>
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes |
| `BETTER_AUTH_SECRET` | JWT secret (must match backend) | Yes |
| `NEXT_PUBLIC_BASE_URL` | Frontend URL | Yes |
| `NODE_ENV` | Environment (development/production) | No |

## Common Issues

### API Connection Errors

If you see "Failed to fetch" errors:

1. Verify backend is running on `http://localhost:8000`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Ensure backend `CORS_ORIGINS` includes `http://localhost:3000`

### Authentication Errors

If JWT authentication fails:

1. Verify `BETTER_AUTH_SECRET` matches backend `JWT_SECRET`
2. Check browser cookies (should have `better-auth.session_token`)
3. Clear cookies and re-authenticate

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

## Development Tips

### Hot Reload

The dev server automatically reloads when you edit:
- Pages in `app/`
- Components in `components/`
- Styles in `app/globals.css`

### TypeScript

All components use TypeScript for type safety. Interfaces are defined in `types/index.ts`:

```typescript
interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
}
```

### API Wrapper

The `apiClient` in `lib/api.ts` handles:
- Automatic JWT attachment
- Error handling
- JSON parsing
- Type safety with generics

## Testing

Currently using manual testing. To add automated tests:

```bash
# Install testing libraries
npm install --save-dev @testing-library/react @testing-library/jest-dom jest

# Run tests
npm test
```

## Deployment

### Vercel (Recommended)

1. Push code to GitHub
2. Import project in Vercel
3. Add environment variables
4. Deploy

### Other Platforms

```bash
# Build static export
npm run build

# Deploy the `.next` folder
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Code splitting with Next.js App Router
- Optimistic UI updates for instant feedback
- Image optimization with `next/image`
- Font optimization with `next/font`

## Accessibility

- Semantic HTML
- ARIA labels on buttons
- Keyboard navigation support
- Focus management

## License

MIT License - see LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
