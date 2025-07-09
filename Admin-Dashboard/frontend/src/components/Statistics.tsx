import React, { useState, useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { Calendar, TrendingUp } from 'lucide-react'
import { format, startOfHour, startOfDay, startOfWeek, startOfMonth, startOfYear } from 'date-fns'
import type { Vehicle, StatsPeriod } from '../types/types'
import '../styles/statistics.css'

interface StatisticsProps {
  vehicles: Vehicle[]
}

const Statistics: React.FC<StatisticsProps> = ({ vehicles }) => {
  const [selectedPeriod, setSelectedPeriod] = useState<'hour' | 'day' | 'week' | 'month' | 'year'>('day')

  const chartData = useMemo(() => {
    const groupedData = new Map<string, { entries: number; exits: number }>()

    vehicles.forEach(vehicle => {
      let key: string
      let periodStart: Date

      switch (selectedPeriod) {
        case 'hour':
          periodStart = startOfHour(vehicle.entryTime)
          key = format(periodStart, 'HH:mm dd/MM')
          break
        case 'day':
          periodStart = startOfDay(vehicle.entryTime)
          key = format(periodStart, 'dd/MM/yyyy')
          break
        case 'week':
          periodStart = startOfWeek(vehicle.entryTime)
          key = format(periodStart, 'dd/MM/yyyy')
          break
        case 'month':
          periodStart = startOfMonth(vehicle.entryTime)
          key = format(periodStart, 'MM/yyyy')
          break
        case 'year':
          periodStart = startOfYear(vehicle.entryTime)
          key = format(periodStart, 'yyyy')
          break
      }

      if (!groupedData.has(key)) {
        groupedData.set(key, { entries: 0, exits: 0 })
      }

      const data = groupedData.get(key)!
      data.entries += 1

      if (vehicle.exitTime) {
        data.exits += 1
      }
    })

    return Array.from(groupedData.entries())
      .map(([period, data]) => ({
        period,
        entries: data.entries,
        exits: data.exits
      }))
      .sort((a, b) => a.period.localeCompare(b.period))
  }, [vehicles, selectedPeriod])

  const totalStats = useMemo(() => {
    const total = vehicles.length
    const exited = vehicles.filter(v => v.status === 'exited').length
    const parked = vehicles.filter(v => v.status === 'parked').length
    
    return { total, exited, parked }
  }, [vehicles])

  return (
    <div className="statistics">
      <div className="statistics-header">
        <h3>Vehicle Statistics</h3>
        <div className="period-selector">
          <label htmlFor="period">Group by:</label>
          <select 
            id="period"
            value={selectedPeriod} 
            onChange={(e) => setSelectedPeriod(e.target.value as any)}
          >
            <option value="hour">Hour</option>
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
          </select>
        </div>
      </div>

      <div className="statistics-summary">
        <div className="summary-card">
          <div className="summary-icon">
            <TrendingUp size={24} />
          </div>
          <div className="summary-content">
            <h4>Total Vehicles</h4>
            <p className="summary-number">{totalStats.total}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">
            <Calendar size={24} />
          </div>
          <div className="summary-content">
            <h4>Currently Parked</h4>
            <p className="summary-number">{totalStats.parked}</p>
          </div>
        </div>
        
        <div className="summary-card">
          <div className="summary-icon">
            <TrendingUp size={24} />
          </div>
          <div className="summary-content">
            <h4>Total Exits</h4>
            <p className="summary-number">{totalStats.exited}</p>
          </div>
        </div>
      </div>

      <div className="charts-container">
        <div className="chart-section">
          <h4>Entries vs Exits by {selectedPeriod}</h4>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="entries" fill="#3B82F6" name="Entries" />
                <Bar dataKey="exits" fill="#10B981" name="Exits" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-section">
          <h4>Trend Analysis</h4>
          <div className="chart-wrapper">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="period" 
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="entries" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  name="Entries"
                />
                <Line 
                  type="monotone" 
                  dataKey="exits" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  name="Exits"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Statistics
