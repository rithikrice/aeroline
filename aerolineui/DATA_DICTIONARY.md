# AeroLine UI - Data Dictionary

## Overview
This document provides a comprehensive reference for all mock data used in the AeroLine UI dashboard application. The data simulates a realistic airline cargo operations and manufacturing supply chain scenario.

---

## Table of Contents
1. [Airports & Locations](#airports--locations)
2. [Manufacturing Facilities](#manufacturing-facilities)
3. [Machines & Equipment](#machines--equipment)
4. [Flights & Shipments](#flights--shipments)
5. [Risk Management](#risk-management)
6. [Operations Teams](#operations-teams)
7. [Spare Parts Inventory](#spare-parts-inventory)
8. [Production Orders](#production-orders)
9. [Financial Metrics](#financial-metrics)
10. [AI Recommendations](#ai-recommendations)
11. [Performance History](#performance-history)

---

## Airports & Locations

### Data Structure
```javascript
{
  code: String,      // IATA airport code (3 letters)
  name: String,      // Full airport name
  city: String,      // City location
  country: String,   // Country
  lat: Number,       // Latitude coordinate
  lng: Number        // Longitude coordinate
}
```

### Sample Airports (15 Total)
- **JFK** - New York, USA
- **LAX** - Los Angeles, USA
- **LHR** - London, UK
- **DXB** - Dubai, UAE
- **SIN** - Singapore
- **HKG** - Hong Kong
- **FRA** - Frankfurt, Germany
- **And 8 more...**

---

## Manufacturing Facilities

### Data Structure
```javascript
{
  id: String,        // Unique facility ID (FAC_XXX_##)
  name: String,      // Facility name
  city: String,      // City location
  country: String,   // Country
  lat: Number,       // Latitude
  lng: Number,       // Longitude
  capacity: Number   // Daily production capacity (units)
}
```

### Sample Facilities (6 Total)
1. **FAC_NYC_01** - Manhattan Assembly Center (Capacity: 5,000 units/day)
2. **FAC_LA_02** - Long Beach Manufacturing Hub (Capacity: 7,500 units/day)
3. **FAC_LON_03** - Heathrow Logistics Park (Capacity: 4,200 units/day)
4. **FAC_DXB_04** - Dubai Industrial City (Capacity: 6,800 units/day)
5. **FAC_DEL_05** - Gurgaon Production Facility (Capacity: 9,200 units/day)
6. **FAC_MUM_06** - Navi Mumbai Tech Park (Capacity: 5,600 units/day)

---

## Machines & Equipment

### Machine Types
- **CNC_MILL** - CNC Milling Machine
- **LASER_CUT** - Laser Cutting System
- **WELDING_ROBOT** - Robotic Welding Station
- **ASSEMBLY_LINE** - Automated Assembly Line
- **QUALITY_SCANNER** - 3D Quality Scanner
- **PRESS_MACHINE** - Hydraulic Press
- **COATING_BOOTH** - Coating & Paint Booth
- **PACKAGING_AUTO** - Automated Packaging System

### Data Structure
```javascript
{
  id: String,             // Machine ID (M-####-X)
  type: String,           // Machine type code
  manufacturer: String,   // Equipment manufacturer
  model: String,          // Model number
  facility: String,       // Facility ID where installed
  installDate: String,    // Installation date (YYYY-MM-DD)
  lastMaintenance: String,// Last maintenance date
  health: Number,         // Health score (0-100)
  status: String          // operational | warning | critical
}
```

### Sample Machines (8 Total)
- **M-1847-A** - Haas VF-4SS CNC Mill (Health: 94%)
- **M-2341-B** - Trumpf TruLaser 5030 (Health: 87%)
- **M-3892-C** - FANUC ARC Mate Welding Robot (Health: 78% ⚠️)
- **M-6234-F** - Schuler SMG 630 Hydraulic Press (Health: 68% 🔴 CRITICAL)

---

## Flights & Shipments

### Flight Statuses
- **on_time** - Flight operating normally
- **delayed** - Minor delay (ETA drift positive)
- **in_transit** - Currently en route
- **arrived** - Completed delivery
- **critical** - Major delay requiring intervention

### Data Structure
```javascript
{
  id: String,                  // Unique flight ID
  airline: String,             // Cargo airline name
  flightNumber: String,        // Flight number
  from: String,                // Origin airport code
  to: String,                  // Destination airport code
  departure: String,           // Departure timestamp
  estimatedArrival: String,    // ETA timestamp
  actualArrival: String,       // Actual arrival (null if in flight)
  etaDrift: Number,           // Minutes ahead/behind schedule (+/-)
  status: String,              // Flight status
  priority: String,            // urgent | high | medium | low
  cargo: String,               // Cargo description
  weight: String,              // Cargo weight
  destinationFacility: String, // Target facility ID
  affectedMachines: Array,     // Machine IDs dependent on this cargo
  trackingCode: String,        // Tracking reference
  route: Array                 // [[lat, lng], ...] waypoints
}
```

### Sample Flights (8 Total)
1. **AX-8472** (JFK→LHR) - Precision parts, 15 min delayed ⚠️
2. **CX-2918** (LAX→NRT) - Electronic components, 5 min early ✓
3. **WC-4521** (FRA→BOM) - Critical spares, 45 min delayed 🔴 CRITICAL
4. **SG-5634** (DXB→DEL) - Hydraulic spares, 8 min delayed
5. **And 4 more active flights...**

**Key Metrics:**
- Average ETA Drift: ~13 minutes
- Critical Delays: 2 flights
- Total Active Cargo: ~76,000 kg

---

## Risk Management

### Risk Severities
- **low** - Minimal impact, monitoring only
- **medium** - Moderate impact, action recommended
- **high** - Significant impact, urgent action required
- **critical** - Severe impact, immediate action required

### Risk Types
- **Flight Delay** - ETA drift impacting operations
- **Machine Failure** - Equipment malfunction imminent
- **Spare Shortage** - Inventory below safety threshold
- **Weather** - Weather disruption affecting routes
- **Customs** - Customs clearance delays
- **Capacity** - Production capacity constraints

### Data Structure
```javascript
{
  id: String,                  // Risk ID (RISK-#####)
  type: String,                // Risk type
  severity: String,            // Severity level
  priority: String,            // Action priority
  flightId: String,            // Related flight ID
  machineId: String,           // Related machine ID
  facility: String,            // Affected facility ID
  riskScore: Number,           // Risk score (0-1)
  detectedAt: String,          // Detection timestamp
  description: String,         // Risk description
  suggestedAction: String,     // AI-recommended action
  alternativeActions: Array,   // Alternative options
  roi: String,                 // ROI of suggested action
  estimatedCost: String,       // Cost to implement action
  estimatedSavings: String,    // Potential savings
  cortexNarrative: String,     // AI-generated explanation
  impactedOrders: Number,      // Number of orders at risk
  impactedRevenue: String,     // Revenue at risk
  probabilityOfDowntime: Number, // Downtime probability (0-1)
  topFeatures: Array,          // Key risk factors
  timeline: Array,             // Event timeline
  assignment: String           // Assigned team
}
```

### Active Risks (5 Total)

#### RISK-10847 - HIGH PRIORITY ⚠️
- **Type:** Flight Delay
- **Flight:** AX-8472 (JFK→LHR)
- **Machine:** M-3892-C (Welding Robot)
- **Risk Score:** 87%
- **Suggested Action:** Expedite flight via priority routing
- **ROI:** 3.8x
- **Cost:** $18,500
- **Savings:** $70,300
- **Impacted Orders:** 47 orders worth $285K

#### RISK-10848 - CRITICAL 🔴
- **Type:** Machine Failure
- **Flight:** WC-4521 (FRA→BOM)
- **Machine:** M-6234-F (Hydraulic Press)
- **Risk Score:** 94%
- **Suggested Action:** Emergency expedite + activate backup capacity
- **ROI:** 4.2x
- **Cost:** $32,800
- **Savings:** $137,760
- **Impacted Orders:** 89 orders worth $542K

---

## Operations Teams

### Data Structure
```javascript
{
  id: String,             // Team ID
  name: String,           // Team name
  lead: String,           // Team lead name
  members: Array,         // Team member names
  specialization: String, // Area of expertise
  activeRisks: Number,    // Currently assigned risks
  avgResponseTime: String,// Average response time
  successRate: String     // Action success rate %
}
```

### Teams (3 Total)
1. **Ops Team Alpha** - Flight Operations & Expediting (94% success)
2. **Ops Team Beta** - Machine Maintenance & Spare Parts (89% success)
3. **Ops Team Gamma** - Customs & Compliance (91% success)

---

## Spare Parts Inventory

### Data Structure
```javascript
{
  partNumber: String,   // Part identifier
  name: String,         // Part name
  category: String,     // Component category
  inStock: Number,      // Current inventory count
  reorderPoint: Number, // Reorder threshold
  leadTime: String,     // Supplier lead time
  unitCost: String,     // Cost per unit
  supplier: String      // Supplier name
}
```

### Sample Parts (8 Categories)
- Hydraulic Cylinder Assembly - 8 in stock (below reorder: 12) ⚠️
- High-Precision Bearing Kit - 24 in stock ✓
- Laser Optics Module - 3 in stock (critical: reorder 8) 🔴
- Servo Motor Assembly - 15 in stock ✓

---

## Production Orders

### Data Structure
```javascript
{
  orderId: String,      // Order ID (PO-#####)
  customer: String,     // Customer company
  product: String,      // Product description
  quantity: Number,     // Order quantity
  dueDate: String,      // Due date
  status: String,       // in_progress | scheduled | completed
  priority: String,     // urgent | high | medium | low
  facility: String,     // Production facility
  atRisk: Boolean       // Risk flag
}
```

### Sample Customers
- Boeing Commercial
- Airbus Operations
- Lockheed Martin
- GE Aviation
- Rolls-Royce
- Safran Aircraft Engines

---

## Financial Metrics

### Key Metrics
```javascript
{
  ytdRevenue: 45,780,000,         // Year-to-date revenue
  ytdCosts: 32,450,000,           // Year-to-date costs
  ytdSavingsFromAI: 3,890,000,    // AI-driven savings
  avgOrderValue: 78,500,          // Average order value
  avgDowntimeCostPerHour: 12,400, // Hourly downtime cost
  avgExpediteFee: 8,900,          // Average expedite fee
  avgDelayPenalty: 15,600,        // Average delay penalty
  monthlyTargets: {
    revenue: 4,200,000,           // Monthly revenue target
    otif: 94.5,                   // OTIF % target
    aiAdoption: 78.0              // AI adoption target %
  }
}
```

---

## AI Recommendations

### Action Types
1. **Expedite Shipment** - Fast-track critical flights
   - Cost: $8,500 - $22,000
   - ROI: 3.2x average
   - Success Rate: 89%

2. **Reschedule Production** - Optimise schedule
   - Cost: $2,200 - $8,900
   - ROI: 2.4x average
   - Success Rate: 82%

3. **Pull Spare Parts** - Source from alternate location
   - Cost: $3,800 - $15,000
   - ROI: 2.8x average
   - Success Rate: 76%

4. **Monitor Only** - Continue observation
   - Cost: $0
   - ROI: N/A
   - Success Rate: 45%

---

## Performance History

### 30-Day Metrics
- **OTIF %:** Ranges 91-95% (Target: 94.5%)
- **Risk Score:** Ranges 68-79 (Lower is better)
- **Flight Delays:** 1-8 per day average
- **Machine Downtime:** 1.5-4.5 hours per day

### 12-Month Financial Trends
- **Revenue:** $3.5M - $4.5M per month (Growing)
- **Costs:** $2.5M - $3.2M per month
- **AI Savings:** $280K - $412K per month (Increasing)

---

## Data Relationships

### Key Connections
1. **Flights** → **Machines** (via `affectedMachines`)
2. **Risks** → **Flights** + **Machines** + **Facilities**
3. **Machines** → **Facilities** (installation location)
4. **Production Orders** → **Facilities** (production location)
5. **Spare Parts** → **Machines** (required components)
6. **Teams** → **Risks** (assignment responsibility)

---

## Realism Features

### What Makes This Data Realistic

1. **Geographic Accuracy**
   - Real airport codes and coordinates
   - Actual airline cargo company naming patterns
   - Realistic flight routes with waypoints

2. **Industry Standards**
   - Authentic machine manufacturers (Haas, Trumpf, FANUC, Siemens, KUKA)
   - Real part numbering schemes
   - Industry-standard maintenance schedules

3. **Financial Reality**
   - Market-accurate costs for expediting ($8K-$22K)
   - Realistic downtime costs ($12.4K/hour)
   - Industry-typical ROI multiples (1.5x - 4.2x)

4. **Operational Patterns**
   - OTIF targets aligned with industry benchmarks (94.5%)
   - Realistic ETA drift patterns (-10 to +45 minutes)
   - Authentic machine health degradation curves

5. **Supply Chain Complexity**
   - Multi-facility dependencies
   - International shipping routes
   - Spare parts lead times (2-14 days)
   - Production capacity constraints

---

## Usage in Application

### Where This Data Appears

1. **Executive Dashboard** - KPIs, charts, activity feed
2. **Risk Engine** - Risk cards, timeline, recommendations
3. **AI Recommendations** - Action cards, ROI analysis
4. **Simulator** - What-if scenarios, cost modeling
5. **GeoMap** - Flight tracking, route visualization
6. **AppLayout** - Navigation, context

---

## Data Maintenance

### Updating Mock Data
The mock data is centralized in `/src/data/mockData.js` for easy updates:

```javascript
import { FLIGHTS, RISKS, MACHINES, ... } from '../data/mockData';
```

### Adding New Data
1. Define new constants in `mockData.js`
2. Export in the default export object
3. Import where needed in components
4. Update this documentation

---

## Version History
- **v1.0** - Initial comprehensive mock data (October 2025)
- Complete dataset covering all application features
- Realistic industry-standard values
- Full relationship mapping

---

**Last Updated:** October 15, 2025
**Maintained By:** AeroLine Development Team
**Contact:** For questions about data structures or adding new mock data, refer to this document or the inline comments in `mockData.js`.

