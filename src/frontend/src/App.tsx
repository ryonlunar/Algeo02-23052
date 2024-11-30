import './App.css';
import Navbar from './components/Navbar'; // Import Navbar

function App() {
  return (
    <div className="App">
      <Navbar />
      <div className="content">
        <h1>Welcome to BRRMusic</h1>
        <p>Explore your favorite music and albums.</p>
      </div>
    </div>
  );
}

export default App;
