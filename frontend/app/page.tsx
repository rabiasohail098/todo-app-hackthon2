"use client";

import Link from "next/link";
import { CheckCircle2, ListTodo, Shield, Zap, Sparkles, Rocket } from "lucide-react";
import { useTranslation } from "@/hooks/useTranslation";
import ThemeToggle from "@/components/ThemeToggle";
import LanguageToggle from "@/components/LanguageToggle";

/**
 * Landing page for the Todo App.
 *
 * Displays hero section, features, and call-to-action buttons.
 */
export default function LandingPage() {
  const t = useTranslation();
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-20 h-20 bg-purple-500/20 rounded-full blur-xl animate-pulse"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-pink-500/20 rounded-full blur-xl animate-pulse delay-75"></div>
        <div className="absolute bottom-40 left-1/4 w-24 h-24 bg-blue-500/20 rounded-full blur-xl animate-pulse delay-150"></div>
        <div className="absolute bottom-20 right-1/3 w-28 h-28 bg-cyan-500/20 rounded-full blur-xl animate-pulse"></div>
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

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-20 relative z-10">
        <div className="text-center space-y-10 mb-20">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 glass px-6 py-3 rounded-full text-fade-up">
            <Sparkles className="w-5 h-5 text-purple-500 dark:text-purple-400" />
            <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
              {t.modernTaskManager}
            </span>
          </div>

          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black heading-animate">
            <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent block mb-4">
              {t.manageTasks}
            </span>
            <span className="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-600 dark:from-blue-400 dark:via-cyan-400 dark:to-teal-400 bg-clip-text text-transparent block">
              {t.stayOrganized}
            </span>
          </h1>

          <p className="text-xl md:text-2xl font-medium max-w-3xl mx-auto text-fade-up text-fade-up-delay-1 bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent">
            {t.beautifulTaskManagement}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center text-fade-up text-fade-up-delay-2">
            <Link
              href="/auth/sign-up"
              className="group relative px-10 py-5 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white font-bold rounded-2xl shadow-2xl transition-all transform hover:scale-110 hover:shadow-purple-500/50 text-lg overflow-hidden"
            >
              <span className="relative z-10 flex items-center gap-2">
                <Rocket className="w-5 h-5" />
                {t.getStartedFree}
              </span>
              <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
            </Link>
            <Link
              href="/auth/sign-in"
              className="px-10 py-5 rounded-2xl font-bold text-lg transition-all transform hover:scale-105 border-2 border-purple-400/50 hover:border-purple-500/80 dark:border-purple-400/30 dark:hover:border-purple-400/50 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent hover:shadow-xl hover:shadow-purple-500/30"
            >
              {t.signIn} →
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Feature 1 */}
          <div className="glass-strong p-8 rounded-3xl card-3d group border-2 border-purple-200/40 hover:border-purple-400/60 dark:border-transparent transition-all">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-6 transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-300 shadow-lg shadow-purple-500/30">
              <ListTodo className="text-white" size={28} />
            </div>
            <h3 className="text-xl font-bold mb-3 bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">
              {t.simpleManagement}
            </h3>
            <p className="text-purple-700 dark:text-purple-300 leading-relaxed font-medium">
              {t.simpleManagementDesc}
            </p>
          </div>

          {/* Feature 2 */}
          <div className="glass-strong p-8 rounded-3xl card-3d group border-2 border-green-200/40 hover:border-green-400/60 dark:border-transparent transition-all">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-500 rounded-2xl flex items-center justify-center mb-6 transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-300 shadow-lg shadow-green-500/30">
              <CheckCircle2 className="text-white" size={28} />
            </div>
            <h3 className="text-xl font-bold mb-3 bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-400 dark:to-emerald-400 bg-clip-text text-transparent">
              {t.trackProgress}
            </h3>
            <p className="text-green-700 dark:text-green-300 leading-relaxed font-medium">
              {t.trackProgressDesc}
            </p>
          </div>

          {/* Feature 3 */}
          <div className="glass-strong p-8 rounded-3xl card-3d group border-2 border-blue-200/40 hover:border-blue-400/60 dark:border-transparent transition-all">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-2xl flex items-center justify-center mb-6 transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-300 shadow-lg shadow-blue-500/30">
              <Shield className="text-white" size={28} />
            </div>
            <h3 className="text-xl font-bold mb-3 bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent">
              {t.securePrivate}
            </h3>
            <p className="text-blue-700 dark:text-blue-300 leading-relaxed font-medium">
              {t.securePrivateDesc}
            </p>
          </div>

          {/* Feature 4 */}
          <div className="glass-strong p-8 rounded-3xl card-3d group border-2 border-orange-200/40 hover:border-orange-400/60 dark:border-transparent transition-all">
            <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl flex items-center justify-center mb-6 transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-300 shadow-lg shadow-orange-500/30">
              <Zap className="text-white" size={28} />
            </div>
            <h3 className="text-xl font-bold mb-3 bg-gradient-to-r from-orange-600 to-red-600 dark:from-orange-400 dark:to-red-400 bg-clip-text text-transparent">
              {t.lightningFast}
            </h3>
            <p className="text-orange-700 dark:text-orange-300 leading-relaxed font-medium">
              {t.lightningFastDesc}
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-32 text-center">
          <h2 className="text-4xl md:text-5xl font-black mb-16 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent heading-animate">
            {t.whyChooseUs}
          </h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="glass-strong p-10 rounded-3xl card-3d border-2 border-green-200/40 hover:border-green-400/60 dark:border-transparent transition-all">
              <div className="text-6xl font-black bg-gradient-to-r from-green-600 to-emerald-600 dark:from-green-400 dark:to-emerald-400 bg-clip-text text-transparent mb-3">
                100%
              </div>
              <div className="text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">{t.freeForever}</div>
            </div>
            <div className="glass-strong p-10 rounded-3xl card-3d border-2 border-blue-200/40 hover:border-blue-400/60 dark:border-transparent transition-all">
              <div className="text-6xl font-black bg-gradient-to-r from-blue-600 to-cyan-600 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent mb-3">
                {t.lessThan2s}
              </div>
              <div className="text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">{t.lightningFast}</div>
            </div>
            <div className="glass-strong p-10 rounded-3xl card-3d border-2 border-purple-200/40 hover:border-purple-400/60 dark:border-transparent transition-all">
              <div className="text-6xl font-black bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent mb-3">
                {t.alwaysAvailable}
              </div>
              <div className="text-lg font-semibold bg-gradient-to-r from-purple-600 to-pink-600 dark:from-purple-400 dark:to-pink-400 bg-clip-text text-transparent">{t.alwaysAvailableText}</div>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <div className="mt-32 text-center glass-strong rounded-[3rem] p-16 shadow-2xl card-3d border-2 border-purple-300/40 hover:border-purple-400/60 dark:border-purple-300/20 transition-all">
          <Sparkles className="w-16 h-16 mx-auto mb-6 text-purple-500 dark:text-purple-400 animate-pulse" />
          <h2 className="text-4xl md:text-5xl font-black mb-6 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent">
            {t.readyToGetOrganized}
          </h2>
          <p className="text-xl md:text-2xl mb-10 font-medium bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent max-w-2xl mx-auto">
            {t.joinToday}
          </p>
          <Link
            href="/auth/sign-up"
            className="group inline-block relative px-12 py-6 bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 hover:from-purple-700 hover:via-pink-700 hover:to-blue-700 text-white font-black rounded-2xl shadow-2xl transition-all transform hover:scale-110 hover:shadow-purple-500/50 text-xl overflow-hidden"
          >
            <span className="relative z-10 flex items-center gap-3">
              <Rocket className="w-6 h-6" />
              {t.createFreeAccount}
              <Sparkles className="w-5 h-5" />
            </span>
            <span className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></span>
          </Link>
        </div>
      </div>
    </div>
  );
}
