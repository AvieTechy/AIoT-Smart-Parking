import React, { useState } from 'react'
import { Search, Calendar, X } from 'lucide-react'
import '../styles/search-filters.css'

interface SearchFiltersProps {
  onSearch: (filters: {
    licensePlate?: string
    dateFrom?: Date
    dateTo?: Date
  }) => void
  onClear: () => void
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ onSearch, onClear }) => {
  const [licensePlate, setLicensePlate] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')

  const handleSearch = () => {
    console.log('SearchFilters: Performing search with:', { licensePlate, dateFrom, dateTo });

    const filters: {
      licensePlate?: string
      dateFrom?: Date
      dateTo?: Date
    } = {}

    if (licensePlate.trim()) {
      filters.licensePlate = licensePlate.trim()
    }

    if (dateFrom) {
      filters.dateFrom = new Date(dateFrom)
    }

    if (dateTo) {
      filters.dateTo = new Date(dateTo + 'T23:59:59')
    }

    console.log('SearchFilters: Calling onSearch with filters:', filters);
    onSearch(filters)
  }

  const handleClear = () => {
    console.log('SearchFilters: Clearing all filters');
    setLicensePlate('')
    setDateFrom('')
    setDateTo('')
    onClear()
  }

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    }
  }

  return (
    <div className="search-filters">
      <div className="search-filters-content">
        <div className="filter-group">
          <label htmlFor="licensePlate">License Plate</label>
          <div className="input-with-icon">
            <Search size={18} className="input-icon" />
            <input
              type="text"
              id="licensePlate"
              placeholder="Enter license plate..."
              value={licensePlate}
              onChange={(e) => setLicensePlate(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="dateFrom">From Date</label>
          <div className="input-with-icon">
            <Calendar size={18} className="input-icon" />
            <div className="date-picker-wrapper">
              <input
                type="date"
                id="dateFrom"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-group">
          <label htmlFor="dateTo">To Date</label>
          <div className="input-with-icon">
            <Calendar size={18} className="input-icon" />
            <div className="date-picker-wrapper">
              <input
                type="date"
                id="dateTo"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="filter-buttons">
          <button className="search-button" onClick={handleSearch}>
            <Search size={18} />
            Search
          </button>
          <button className="clear-button" onClick={handleClear}>
            <X size={18} />
            Clear
          </button>
        </div>
      </div>
    </div>
  )
}

export default SearchFilters
