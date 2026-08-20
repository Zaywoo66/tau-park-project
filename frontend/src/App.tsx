// src/App.tsx
// Core application wrapper managing logical layout sequencing.

import Header from './components/Header';
import Hero from './components/Hero';
import OverviewGrid from './components/OverviewGrid'; // <--- Imported new section
import FeatureBlock from './components/FeatureBlock';
import Houses from './components/Houses';
import Footer from './components/Footer';

function App() {
  return (
    <div className="w-full">
      <Header />
      <main>
        <Hero />
        <OverviewGrid /> {/* <--- Inserted right after Hero */}
        <FeatureBlock />
        <Houses />
      </main>
      <Footer />
    </div>
  );
}

export default App;