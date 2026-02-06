"use client";

import React from "react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { useApp } from "@/context/AppContext";

type ChartType = "bar" | "pie" | "line";

interface StatisticsChartProps {
  data: any[];
  type: ChartType;
  dataKey?: string;
  xAxisKey?: string;
  title?: string;
  colors?: string[];
  className?: string;
}

const DEFAULT_COLORS = [
  "#8b5cf6", // purple-600
  "#ec4899", // pink-600
  "#3b82f6", // blue-600
  "#10b981", // green-600
  "#f59e0b", // amber-600
  "#ef4444", // red-600
];

const StatisticsChart: React.FC<StatisticsChartProps> = ({
  data,
  type,
  dataKey = "value",
  xAxisKey = "name",
  title,
  colors = DEFAULT_COLORS,
  className = "",
}) => {
  const { language } = useApp();

  if (!data || data.length === 0) {
    return (
      <div className={`glass rounded-2xl p-6 text-center ${className}`}>
        <p className="text-zinc-500 dark:text-zinc-400">
          {language === "ur" ? "ڈیٹا دستیاب نہیں" : "No data available"}
        </p>
      </div>
    );
  }

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#71717a"
          style={{ fontSize: "12px" }}
        />
        <YAxis stroke="#71717a" style={{ fontSize: "12px" }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            padding: "8px",
          }}
        />
        <Legend />
        <Bar dataKey={dataKey} fill={colors[0]} radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );

  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) =>
            `${name} (${((percent ?? 0) * 100).toFixed(0)}%)`
          }
          outerRadius={100}
          fill="#8884d8"
          dataKey={dataKey}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            padding: "8px",
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey={xAxisKey}
          stroke="#71717a"
          style={{ fontSize: "12px" }}
        />
        <YAxis stroke="#71717a" style={{ fontSize: "12px" }} />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(255, 255, 255, 0.95)",
            border: "1px solid #e5e7eb",
            borderRadius: "8px",
            padding: "8px",
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={colors[0]}
          strokeWidth={2}
          dot={{ fill: colors[0], r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );

  return (
    <div className={`glass rounded-2xl p-6 ${className}`}>
      {title && (
        <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-4">
          {title}
        </h3>
      )}
      {type === "bar" && renderBarChart()}
      {type === "pie" && renderPieChart()}
      {type === "line" && renderLineChart()}
    </div>
  );
};

export default StatisticsChart;
