# AeroLine UI - Airline Cargo Operations Dashboard

This project is a comprehensive airline cargo operations and manufacturing supply chain management dashboard, powered by AI-driven recommendations and real-time risk analytics.

## 🎯 Features

- **Executive Dashboard** - Real-time KPIs, AI recommendations, and performance metrics
- **Risk Engine** - Comprehensive risk tracking for flights and manufacturing equipment
- **AI Recommendations** - ML-powered prescriptive actions with ROI analysis
- **What-If Simulator** - Interactive scenario modeling for decision support
- **Live Flight Tracking** - Real-time geolocation of cargo flights with detailed cargo info
- **Realistic Mock Data** - Industry-standard data covering 15 airports, 8 flights, 8 machines, 6 facilities, and more

## 📊 Mock Data Overview

This application features **comprehensive, realistic mock data** that simulates actual airline cargo operations:

- ✈️ **8 Active Flights** across global routes (JFK, LAX, LHR, DXB, SIN, etc.)
- 🏭 **6 Manufacturing Facilities** with real capacity metrics
- 🤖 **8 Industrial Machines** from real manufacturers (FANUC, Haas, Trumpf, Siemens, KUKA)
- ⚠️ **5 Active Risk Scenarios** with detailed AI analysis
- 📦 **8 Spare Part Categories** with inventory tracking
- 💰 **12 Months of Financial History** with trending data
- 👥 **3 Operations Teams** with performance metrics

See [DATA_DICTIONARY.md](./DATA_DICTIONARY.md) for complete documentation of all mock data structures.

---

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in your browser.

The page will reload when you make changes.\
You may also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimises the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can't go back!**

If you aren't satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you're on your own.

You don't have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn't feel obligated to use this feature. However we understand that this tool wouldn't be useful if you couldn't customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: [https://facebook.github.io/create-react-app/docs/code-splitting](https://facebook.github.io/create-react-app/docs/code-splitting)

### Analyzing the Bundle Size

This section has moved here: [https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size](https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size)

### Making a Progressive Web App

This section has moved here: [https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app](https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app)

### Advanced Configuration

This section has moved here: [https://facebook.github.io/create-react-app/docs/advanced-configuration](https://facebook.github.io/create-react-app/docs/advanced-configuration)

### Deployment

This section has moved here: [https://facebook.github.io/create-react-app/docs/deployment](https://facebook.github.io/create-react-app/docs/deployment)

### `npm run build` fails to minify

This section has moved here: [https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify](https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify)

---

## 🗂️ Project Structure

```
aerolineui/
├── src/
│   ├── data/
│   │   └── mockData.js          # Centralized realistic mock data
│   ├── screens/
│   │   ├── HomeScreen.js         # Executive Dashboard
│   │   ├── ExecutiveDashboard.js # Risk Engine
│   │   ├── AIScreen.js           # AI Recommendations
│   │   ├── Simulator.js          # What-If Simulator
│   │   ├── GeoMap.js             # Live Flight Tracking
│   │   ├── Login.js              # Authentication
│   │   └── AppLayout.js          # App Navigation Layout
│   ├── components/
│   │   └── ui/                   # Reusable UI components
│   └── ...
├── DATA_DICTIONARY.md            # Complete data documentation
└── README.md                     # This file
```

## 📈 Key Technologies

- **React 19** - Modern React with hooks
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling
- **Chart.js & Recharts** - Data visualization
- **Framer Motion** - Smooth animations
- **React Leaflet** - Interactive maps
- **Lucide React** - Modern icon library

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

4. **Login (optional):**
   The login page allows you to enter the dashboard. Authentication is currently mock-only.

## 📱 Application Pages

### 1. Executive Dashboard (`/dashboard`)
- Real-time OTIF % metrics
- Active risk counts (High/Medium/Low)
- YTD savings from AI recommendations
- Cost trends and delay analytics
- Recent AI activity feed

### 2. Risk Engine (`/risk`)
- Comprehensive risk cards with severity indicators
- Risk trend visualization (30-day history)
- Risk breakdown pie chart
- Detailed risk panel with timeline and explainability
- Top risky flights and machines table
- Filterable by severity, facility, and team

### 3. AI Recommendations (`/ai`)
- Four action types: Expedite, Reschedule, Pull Spares, Monitor
- Detailed cost/savings/ROI analysis
- Success rate probabilities
- Use case recommendations
- Real-time AI narrative from Cortex

### 4. What-If Simulator (`/simulator`)
- Interactive parameter sliders (downtime, expedite costs, penalties)
- 30-day ROI projection chart
- Cost vs. Speed trade-off analysis
- AI-powered insights based on parameters
- Quick scenario buttons (Best/Typical/Worst case)

### 5. Live Flight Map (`/map`)
- Real-time flight tracking on interactive map
- Flight status indicators (On Time, Delayed, Critical)
- ETA drift monitoring
- Cargo details and tracking codes
- Affected machines visibility
- Timeline of flight events

## 🎨 Design System

- **Color Palette:**
  - Primary: Teal (#14b8a6)
  - Background: Dark Navy (#0a192f)
  - Accent: Cyan (#00f5d4)
  - Success: Green (#10b981)
  - Warning: Amber (#f59e0b)
  - Error: Red (#ef4444)

- **Typography:** System fonts with custom font weights
- **Spacing:** Tailwind's 8px grid system
- **Animations:** Subtle hover effects and page transitions via Framer Motion

## 💡 Realistic Mock Data Features

### What Makes This Data Realistic?

1. **Real Geographic Data**
   - Authentic IATA airport codes (JFK, LAX, LHR, DXB, etc.)
   - Actual GPS coordinates for airports and facilities
   - Realistic flight routes with waypoints

2. **Industry-Standard Equipment**
   - Real manufacturers: Haas Automation, Trumpf, FANUC, Siemens, KUKA, Zeiss
   - Actual model numbers and equipment specifications
   - Authentic maintenance schedules and health metrics

3. **Accurate Financial Models**
   - Industry-typical expedite costs ($8K-$22K range)
   - Realistic downtime costs ($12.4K/hour)
   - Market-accurate ROI multiples (1.5x - 4.2x)
   - Authentic order values and revenue figures

4. **Real-World Customers**
   - Boeing Commercial
   - Airbus Operations
   - Lockheed Martin
   - GE Aviation
   - Rolls-Royce
   - Safran Aircraft Engines

5. **Operational Realism**
   - OTIF targets matching industry benchmarks (94.5%)
   - Realistic ETA drift patterns
   - Authentic supply chain lead times (2-14 days)
   - Complex multi-facility dependencies

## 🔧 Customization

### Adding New Mock Data

All mock data is centralized in `/src/data/mockData.js`. To add new data:

1. Define your data structure in `mockData.js`
2. Add it to the default export object
3. Import it in your component:
   ```javascript
   import { FLIGHTS, RISKS, MACHINES } from '../data/mockData';
   ```
4. Update `DATA_DICTIONARY.md` with documentation

### Modifying Existing Data

Edit `/src/data/mockData.js` to:
- Add more flights, machines, or facilities
- Adjust financial metrics
- Create new risk scenarios
- Update performance history data

## 📚 Documentation

- **[DATA_DICTIONARY.md](./DATA_DICTIONARY.md)** - Complete reference for all mock data structures, relationships, and usage
- **Inline Comments** - Each screen has detailed comments explaining data flow and logic

## 🌟 Demo Credentials

The application currently uses mock authentication. Any email/password combination will grant access to the dashboard.

## 🤝 Contributing

This is a demo/prototype application. For production use:
1. Replace mock data with real API endpoints
2. Implement proper authentication
3. Add proper error handling
4. Set up state management (Redux/Context)
5. Add comprehensive testing

## 📄 License

This project is for demonstration purposes.

## 🎓 Technologies & Credits

Built with:
- React & React Router
- Tailwind CSS for styling
- Chart.js & Recharts for data visualization
- Framer Motion for animations
- React Leaflet for mapping
- Lucide React for icons
- Mock data inspired by real airline cargo operations

---

**Last Updated:** October 15, 2025
**Version:** 1.0.0
