"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signUp } from "@/lib/auth-client";
import { FormError } from "@/types";
import { UserPlus, Mail, Lock, Sparkles } from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";
import LanguageToggle from "@/components/LanguageToggle";
import { useTranslation } from "@/hooks/useTranslation";

/**
 * Sign-up page for new user registration.
 *
 * Allows users to create accounts with email and password.
 */
export default function SignUpPage() {
  const router = useRouter();
  const t = useTranslation();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<FormError[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Validate email format using regex.
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Validate form data.
   */
  const validateForm = (): boolean => {
    const newErrors: FormError[] = [];

    // Email validation
    if (!formData.email.trim()) {
      newErrors.push({ field: "email", message: t.emailRequired });
    } else if (!validateEmail(formData.email)) {
      newErrors.push({ field: "email", message: t.invalidEmail });
    }

    // Password validation
    if (!formData.password) {
      newErrors.push({ field: "password", message: t.passwordRequired });
    } else if (formData.password.length < 8) {
      newErrors.push({
        field: "password",
        message: t.passwordMinLength,
      });
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      newErrors.push({
        field: "confirmPassword",
        message: t.confirmPasswordRequired,
      });
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.push({
        field: "confirmPassword",
        message: t.passwordsDoNotMatch,
      });
    }

    setErrors(newErrors);
    return newErrors.length === 0;
  };

  /**
   * Handle form submission.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors([]);

    // Validate
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call Better Auth sign-up
      const result = await signUp.email({
        email: formData.email,
        password: formData.password,
        name: formData.email.split("@")[0], // Use email prefix as name
      });

      console.log("Sign-up result:", JSON.stringify(result, null, 2));

      if (result?.error) {
        console.error("Sign-up error:", result.error);
        throw new Error(result.error.message || "Sign up failed");
      }

      // HuggingFace proxy may strip Set-Cookie headers
      // Try to extract token from various response structures
      const token = result?.data?.token ||
                    result?.data?.session?.token ||
                    result?.data?.session?.id ||
                    result?.token;

      if (token) {
        // Set cookie with appropriate attributes for HuggingFace
        const isSecure = window.location.protocol === 'https:';
        const cookieValue = `better-auth.session_token=${token}; path=/; max-age=86400; SameSite=Lax${isSecure ? '; Secure' : ''}`;
        document.cookie = cookieValue;
        console.log("Cookie set manually:", cookieValue);
      } else {
        console.log("No token found in response, relying on server-side cookie");
      }

      // Small delay to ensure cookie is set before redirect
      await new Promise(resolve => setTimeout(resolve, 100));

      // Full page reload to ensure cookie is picked up by middleware
      window.location.href = "/dashboard";
    } catch (error: any) {
      // Handle sign-up errors
      const errorMessage =
        error.message || t.accountCreationFailed;

      // Check for duplicate email error
      if (
        errorMessage.includes("already exists") ||
        errorMessage.includes("duplicate")
      ) {
        setErrors([
          {
            field: "email",
            message: t.accountExists,
          },
        ]);
      } else {
        setErrors([{ field: "general", message: errorMessage }]);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getFieldError = (field: string) =>
    errors.find((err) => err.field === field)?.message;

  return (
    <div className="min-h-screen flex items-center justify-center p-6 relative overflow-hidden">
      {/* Animated particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-purple-500/20 rounded-full blur-2xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-pink-500/20 rounded-full blur-2xl animate-pulse delay-75"></div>
        <div className="absolute top-1/2 left-1/2 w-36 h-36 bg-blue-500/20 rounded-full blur-2xl animate-pulse delay-150"></div>
      </div>

      {/* Theme and Language Toggles */}
      <div className="absolute top-6 right-6 flex gap-3 z-20">
        <div className="glass-strong rounded-xl p-2">
          <ThemeToggle />
        </div>
        <div className="glass-strong rounded-xl p-2">
          <LanguageToggle />
        </div>
      </div>

      <div className="w-full max-w-md relative z-10 fade-in">
        {/* Header */}
        <div className="text-center mb-10 heading-animate">
          <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
            <Sparkles className="w-4 h-4 text-purple-500 dark:text-purple-400" />
            <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
              {t.joinUsToday}
            </span>
          </div>
          <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent mb-3">
            {t.createAccount}
          </h1>
          <p className="text-lg font-medium bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent">
            {t.startManagingTasks}
          </p>
        </div>

        {/* Sign-up Form */}
        <div className="glass-strong rounded-3xl p-8 card-3d">
          {/* General Error */}
          {getFieldError("general") && (
            <div className="mb-6 p-4 glass rounded-2xl border-2 border-red-400/50 fade-in">
              <p className="font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">
                {getFieldError("general")}
              </p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Input */}
            <div className="text-fade-up">
              <label
                htmlFor="email"
                className="block text-sm font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent"
              >
                {t.emailAddress}
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-500 dark:text-purple-400" />
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  className="w-full pl-12 pr-4 py-4 glass rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all font-medium text-zinc-800 dark:text-zinc-100"
                  placeholder="you@example.com"
                  disabled={isLoading}
                  autoComplete="email"
                />
              </div>
              {getFieldError("email") && (
                <p className="mt-2 text-sm font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">
                  {getFieldError("email")}
                </p>
              )}
            </div>

            {/* Password Input */}
            <div className="text-fade-up text-fade-up-delay-1">
              <label
                htmlFor="password"
                className="block text-sm font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent"
              >
                {t.password}
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-500 dark:text-purple-400" />
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) =>
                    setFormData({ ...formData, password: e.target.value })
                  }
                  className="w-full pl-12 pr-4 py-4 glass rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all font-medium text-zinc-800 dark:text-zinc-100"
                  placeholder={t.minimumChars}
                  disabled={isLoading}
                  autoComplete="new-password"
                />
              </div>
              {getFieldError("password") && (
                <p className="mt-2 text-sm font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">
                  {getFieldError("password")}
                </p>
              )}
            </div>

            {/* Confirm Password Input */}
            <div className="text-fade-up text-fade-up-delay-2">
              <label
                htmlFor="confirmPassword"
                className="block text-sm font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent"
              >
                {t.confirmPassword}
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-500 dark:text-purple-400" />
                <input
                  id="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={(e) =>
                    setFormData({ ...formData, confirmPassword: e.target.value })
                  }
                  className="w-full pl-12 pr-4 py-4 glass rounded-2xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all font-medium text-zinc-800 dark:text-zinc-100"
                  placeholder={t.reEnterPassword}
                  disabled={isLoading}
                  autoComplete="new-password"
                />
              </div>
              {getFieldError("confirmPassword") && (
                <p className="mt-2 text-sm font-semibold bg-gradient-to-r from-red-600 to-pink-600 dark:from-red-400 dark:to-pink-400 bg-clip-text text-transparent">
                  {getFieldError("confirmPassword")}
                </p>
              )}
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="group w-full relative px-8 py-5 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white font-bold rounded-2xl shadow-2xl transition-all transform hover:scale-105 hover:shadow-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden text-fade-up text-fade-up-delay-3"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                <UserPlus className="w-5 h-5" />
                {isLoading ? t.creatingAccount : t.signUp}
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
            </button>
          </form>

          {/* Sign-in Link */}
          <div className="mt-8 text-center text-fade-up text-fade-up-delay-4">
            <p className="text-sm font-medium">
              <span className="text-purple-700 dark:text-purple-300">{t.alreadyHaveAccount}</span>{" "}
              <Link
                href="/auth/sign-in"
                className="font-bold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent hover:from-pink-600 hover:to-purple-600 transition-all"
              >
                {t.signIn} →
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="mt-6 text-center">
          <Link
            href="/"
            className="inline-flex items-center justify-center gap-2 px-6 py-3 border-2 border-purple-400/50 hover:border-purple-500/80 dark:border-purple-400/30 dark:hover:border-purple-400/50 rounded-2xl font-semibold transition-all transform hover:scale-105 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent hover:shadow-lg hover:shadow-purple-500/30"
          >
            ← {t.backToHome}
          </Link>
        </div>
      </div>
    </div>
  );
}
