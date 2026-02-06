"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, TrendingUp, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { authFetch } from "@/lib/api";
import StatisticsChart from "@/components/StatisticsChart";

interface OverallStats {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  completion_rate: number;
  overdue_tasks: number;
  due_today: number;
  due_this_week: number;
}

interface DailyStats {
  date: string;
  created_count: number;
  completed_count: number;
}

interface CategoryDistribution {
  category_id: number;
  category_name: string;
  task_count: number;
  completed_count: number;
  completion_rate: number;
}

interface PriorityDistribution {
  priority: string;
  task_count: number;
  completed_count: number;
  completion_rate: number;
}

/**
 * Statistics dashboard page.
 *
 * Displays task productivity statistics and charts.
 */
export default function StatisticsPage() {
  const router = useRouter();
  const { language, backgroundMode } = useApp();
  const [overallStats, setOverallStats] = useState<OverallStats | null>(null);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [categoryDist, setCategoryDist] = useState<CategoryDistribution[]>([]);
  const [priorityDist, setPriorityDist] = useState<PriorityDistribution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<number>(30); // days

  // Update body class based on background mode
  useEffect(() => {
    document.body.classList.remove('with-background', 'with-background-image');
    if (backgroundMode === 'gradient') {
      document.body.classList.add('with-background');
    } else if (backgroundMode === 'image') {
      document.body.classList.add('with-background-image');
    }
  }, [backgroundMode]);

  useEffect(() => {
    fetchStatistics();
  }, [dateRange]);

  const fetchStatistics = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - dateRange);

      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];

      // Fetch all statistics in parallel
      const [overallRes, dailyRes, categoryRes, priorityRes] = await Promise.all([
        authFetch(`/api/statistics?start_date=${startDateStr}&end_date=${endDateStr}`),
        authFetch(`/api/statistics/daily?start_date=${startDateStr}&end_date=${endDateStr}`),
        authFetch(`/api/statistics/categories`),
        authFetch(`/api/statistics/priorities`),
      ]);

      if (!overallRes.ok || !dailyRes.ok || !categoryRes.ok || !priorityRes.ok) {
        throw new Error("Failed to fetch statistics");
      }

      const [overall, daily, categories, priorities] = await Promise.all([
        overallRes.json(),
        dailyRes.json(),
        categoryRes.json(),
        priorityRes.json(),
      ]);

      setOverallStats(overall);
      setDailyStats(daily);
      setCategoryDist(categories);
      setPriorityDist(priorities);
    } catch (err: any) {
      setError(err.message || "Failed to fetch statistics");
    } finally {
      setIsLoading(false);
    }
  };

  const StatCard = ({
    title,
    value,
    icon: Icon,
    color,
    subtitle,
  }: {
    title: string;
    value: number | string;
    icon: any;
    color: string;
    subtitle?: string;
  }) => (
    <div className="glass rounded-2xl p-6 transition-all hover:scale-105">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
          {title}
        </h3>
        <Icon size={24} className={color} />
      </div>
      <div className="text-3xl font-bold text-zinc-900 dark:text-zinc-100 mb-1">
        {value}
      </div>
      {subtitle && (
        <p className="text-xs text-zinc-500 dark:text-zinc-500">{subtitle}</p>
      )}
    </div>
  );

  return (
    <div className="min-h-screen transition-colors duration-300">
      <div className="max-w-7xl mx-auto p-6 space-y-8 fade-in">
        {/* Header */}
        <header className="flex flex-col sm:flex-row justify-between items-center py-8 gap-6 glass-strong rounded-3xl px-8">
          <div className="text-center sm:text-left">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="p-2 glass hover:glass-strong rounded-xl transition-all"
                aria-label="Back to dashboard"
              >
                <ArrowLeft size={24} className="text-purple-600 dark:text-purple-400" />
              </button>
              <div>
                <h1 className="text-5xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 dark:from-purple-400 dark:via-pink-400 dark:to-blue-400 bg-clip-text text-transparent heading-animate">
                  {language === "ur" ? "شماریات" : "Statistics"}
                </h1>
                <p className="mt-3 text-lg font-medium bg-gradient-to-r from-purple-500 to-pink-500 dark:from-purple-300 dark:to-pink-300 bg-clip-text text-transparent">
                  {language === "ur"
                    ? "اپنی پیداواری صلاحیت کو ٹریک کریں"
                    : "Track your productivity"}
                </p>
              </div>
            </div>
          </div>

          {/* Date Range Filter */}
          <div className="flex gap-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setDateRange(days)}
                className={`px-4 py-2 rounded-xl transition-all ${
                  dateRange === days
                    ? "glass-strong text-purple-600 dark:text-purple-400"
                    : "glass hover:glass-strong"
                }`}
              >
                {days} {language === "ur" ? "دن" : "days"}
              </button>
            ))}
          </div>
        </header>

        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg fade-in">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12 fade-in">
            <p className="text-zinc-500 dark:text-zinc-400">
              {language === "ur" ? "لوڈ ہو رہا ہے..." : "Loading statistics..."}
            </p>
          </div>
        )}

        {/* Statistics Content */}
        {!isLoading && overallStats && (
          <>
            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title={language === "ur" ? "کل کام" : "Total Tasks"}
                value={overallStats.total_tasks}
                icon={TrendingUp}
                color="text-blue-600 dark:text-blue-400"
                subtitle={`${overallStats.completed_tasks} completed`}
              />
              <StatCard
                title={language === "ur" ? "تکمیل کی شرح" : "Completion Rate"}
                value={`${overallStats.completion_rate}%`}
                icon={CheckCircle}
                color="text-green-600 dark:text-green-400"
                subtitle={`${overallStats.pending_tasks} pending`}
              />
              <StatCard
                title={language === "ur" ? "آج کی مدت ختم" : "Due Today"}
                value={overallStats.due_today}
                icon={Clock}
                color="text-amber-600 dark:text-amber-400"
                subtitle={`${overallStats.due_this_week} this week`}
              />
              <StatCard
                title={language === "ur" ? "مدت ختم" : "Overdue"}
                value={overallStats.overdue_tasks}
                icon={AlertCircle}
                color="text-red-600 dark:text-red-400"
                subtitle="Requires attention"
              />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Daily Activity Chart */}
              <StatisticsChart
                type="line"
                data={dailyStats.map((d) => ({
                  name: new Date(d.date).toLocaleDateString(
                    language === "ur" ? "ur-PK" : "en-US",
                    { month: "short", day: "numeric" }
                  ),
                  Created: d.created_count,
                  Completed: d.completed_count,
                }))}
                dataKey="Created"
                xAxisKey="name"
                title={
                  language === "ur"
                    ? "روزانہ سرگرمی"
                    : "Daily Activity"
                }
              />

              {/* Category Distribution */}
              <StatisticsChart
                type="pie"
                data={categoryDist.map((c) => ({
                  name: c.category_name,
                  value: c.task_count,
                }))}
                title={
                  language === "ur"
                    ? "زمرہ کی تقسیم"
                    : "Category Distribution"
                }
              />

              {/* Priority Distribution */}
              <StatisticsChart
                type="bar"
                data={priorityDist.map((p) => ({
                  name: p.priority.charAt(0).toUpperCase() + p.priority.slice(1),
                  "Task Count": p.task_count,
                  "Completion Rate": p.completion_rate,
                }))}
                dataKey="Task Count"
                xAxisKey="name"
                title={
                  language === "ur"
                    ? "ترجیح کی تقسیم"
                    : "Priority Distribution"
                }
              />

              {/* Completion Trend */}
              <StatisticsChart
                type="line"
                data={dailyStats.map((d) => ({
                  name: new Date(d.date).toLocaleDateString(
                    language === "ur" ? "ur-PK" : "en-US",
                    { month: "short", day: "numeric" }
                  ),
                  value: d.completed_count,
                }))}
                dataKey="value"
                xAxisKey="name"
                title={
                  language === "ur"
                    ? "تکمیل کا رجحان"
                    : "Completion Trend"
                }
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}
