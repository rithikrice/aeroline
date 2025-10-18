import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './MatrixMode.css';

const MATRIX_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$+-*/=%"\'#&_(),.;:?!\\|{}<>[]^~';
const SQL_QUERIES = [
  'SELECT flight_id, status, eta_drift FROM flights WHERE status = \'critical\'',
  'ANALYZE risk_factors JOIN facility_metrics ON facility_id',
  'CALL snowflake.cortex.predict_delay(flight_data, weather_data)',
  'SELECT AVG(otif_score) FROM performance_history WHERE date > CURRENT_DATE - 30',
  'UPDATE optimisation_engine SET mode = \'emergency\' WHERE priority = \'high\'',
];

export default function MatrixMode({ onExit, onCommandExecute }) {
  const [showTerminal, setShowTerminal] = useState(false);
  const [terminalOutput, setTerminalOutput] = useState([]);
  const [currentCommand, setCurrentCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [neuralActivity, setNeuralActivity] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [position, setPosition] = useState(() => ({
    x: window.innerWidth / 2,
    y: window.innerHeight / 2
  }));
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const inputRef = useRef(null);
  const outputRef = useRef(null);
  const terminalRef = useRef(null);

  useEffect(() => {
    // Show terminal after rain effect
    const timer = setTimeout(() => {
      setShowTerminal(true);
      addOutput('> SYSTEM: Matrix Mode Activated');
      addOutput('> AI Core: Snowflake Cortex Online');
      addOutput('> Type "help" for commands or "exit" to return');
      addOutput('');
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (showTerminal && inputRef.current) {
      inputRef.current.focus();
    }
  }, [showTerminal]);

  const addOutput = (text) => {
    setTerminalOutput(prev => [...prev, text]);
  };

  // Auto-scroll to bottom when new output is added
  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight;
    }
  }, [terminalOutput]);

  const executeCommand = (cmd) => {
    const command = cmd.trim().toLowerCase();
    addOutput(`> ${cmd}`);

    if (command === 'exit') {
      addOutput('> Exiting Matrix Mode...');
      setTimeout(onExit, 1000);
      return;
    }

    if (command === 'help') {
      addOutput('');
      addOutput('Available Commands:');
      addOutput('  analyze <flight>  - Analyze flight risk in real-time');
      addOutput('  optimise          - Run AI optimisation');
      addOutput('  query             - Show SQL query to Snowflake');
      addOutput('  neural            - Display neural network activity');
      addOutput('  exit              - Return to normal view');
      addOutput('');
      return;
    }

    if (command.startsWith('analyze')) {
      const flightId = command.split(' ')[1] || 'FL-8472';
      setIsProcessing(true);
      setNeuralActivity(true);
      
      addOutput('');
      addOutput(`> Analyzing flight ${flightId.toUpperCase()}...`);
      addOutput('> Querying Snowflake data warehouse...');
      
      setTimeout(() => {
        addOutput('> [SQL] ' + SQL_QUERIES[0]);
        addOutput('> Processing 47 risk factors...');
      }, 500);
      
      setTimeout(() => {
        addOutput('> Neural network activated...');
        addOutput('> Confidence: 94.7%');
        addOutput('> Risk Level: HIGH');
        addOutput('> Recommendation: Expedite routing');
        addOutput('> Estimated savings: $87,000');
        addOutput('> Analysis complete.');
        addOutput('');
        setIsProcessing(false);
        setNeuralActivity(false);
        
        if (onCommandExecute) {
          onCommandExecute('analyze', flightId);
        }
      }, 2500);
      return;
    }

    if (command === 'optimise') {
      setIsProcessing(true);
      addOutput('');
      addOutput('> Initializing global optimisation...');
      
      setTimeout(() => {
        addOutput('> [SQL] ' + SQL_QUERIES[2]);
        addOutput('> Cortex AI: Analyzing all active routes...');
        addOutput('> Processing: 47 flights, 12 facilities, 234 machines');
      }, 500);
      
      setTimeout(() => {
        addOutput('> Optimisation complete!');
        addOutput('> Routes optimised: 15');
        addOutput('> Projected savings: $247,000');
        addOutput('> OTIF improvement: +4.2%');
        addOutput('');
        setIsProcessing(false);
        
        if (onCommandExecute) {
          onCommandExecute('optimise');
        }
      }, 2000);
      return;
    }

    if (command === 'query') {
      addOutput('');
      addOutput('> Live Snowflake Queries:');
      SQL_QUERIES.forEach((query, i) => {
        setTimeout(() => {
          addOutput(`> [${i + 1}] ${query}`);
        }, i * 300);
      });
      setTimeout(() => addOutput(''), SQL_QUERIES.length * 300 + 100);
      return;
    }

    if (command === 'neural') {
      setNeuralActivity(!neuralActivity);
      addOutput(`> Neural network visualization: ${!neuralActivity ? 'ENABLED' : 'DISABLED'}`);
      addOutput('');
      return;
    }

    // Unknown command
    addOutput(`> Error: Unknown command "${cmd}"`);
    addOutput('> Type "help" for available commands');
    addOutput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && currentCommand.trim()) {
      executeCommand(currentCommand);
      setCurrentCommand('');
    }
  };

  const handleEscape = (e) => {
    if (e.key === 'Escape') {
      onExit();
    }
  };

  useEffect(() => {
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Dragging handlers
  const handleHeaderMouseDown = (e) => {
    if (!terminalRef.current) return;
    
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
    e.preventDefault();
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      
      e.preventDefault();
      
      setPosition({
        x: e.clientX - dragOffset.x,
        y: e.clientY - dragOffset.y
      });
    };

    const handleMouseUp = (e) => {
      if (isDragging) {
        e.preventDefault();
        setIsDragging(false);
      }
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove, { passive: false });
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragOffset.x, dragOffset.y]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="matrix-overlay"
    >
      {/* Matrix Rain Background */}
      <div className="matrix-rain-container">
        {Array.from({ length: 50 }).map((_, i) => (
          <div
            key={i}
            className="matrix-column"
            style={{
              animationDuration: `${Math.random() * 3 + 2}s`,
              animationDelay: `${Math.random() * 2}s`,
              opacity: Math.random() * 0.5 + 0.3,
            }}
          >
            {Array.from({ length: 30 }).map((_, j) => (
              <div key={j}>
                {MATRIX_CHARS[Math.floor(Math.random() * MATRIX_CHARS.length)]}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Terminal */}
      <AnimatePresence>
        {showTerminal && (
          <motion.div
            ref={terminalRef}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="matrix-terminal"
            style={{
              left: `${position.x}px`,
              top: `${position.y}px`,
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'auto'
            }}
          >
            <div 
              className="matrix-terminal-header" 
              style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
              onMouseDown={handleHeaderMouseDown}
            >
              <div className="matrix-terminal-title">
                ◈ SNOWFLAKE CORTEX AI :: MATRIX INTERFACE ◈
              </div>
              <div style={{ fontSize: '12px', opacity: 0.7 }}>
                Drag header to move
              </div>
            </div>

            <div className="matrix-terminal-output" ref={outputRef}>
              {terminalOutput.map((line, i) => (
                <div key={i} className="matrix-terminal-line">
                  {line.startsWith('> [SQL]') ? (
                    <div className="sql-query-display">
                      {line.replace('> [SQL] ', '')}
                    </div>
                  ) : (
                    line
                  )}
                </div>
              ))}
              {isProcessing && (
                <div className="matrix-terminal-line">
                  <span className="matrix-terminal-prompt">{'> '}</span>
                  <span>Processing...</span>
                  <span className="matrix-terminal-cursor" />
                </div>
              )}
            </div>

            <div className="matrix-terminal-input-container">
              <span className="matrix-terminal-prompt">{'> '}</span>
              <input
                ref={inputRef}
                type="text"
                className="matrix-terminal-input"
                value={currentCommand}
                onChange={(e) => setCurrentCommand(e.target.value)}
                onKeyDown={handleKeyDown}
                disabled={isProcessing}
                placeholder="Type command..."
              />
              {!isProcessing && <span className="matrix-terminal-cursor" />}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Neural Network Visualization */}
      <AnimatePresence>
        {neuralActivity && (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className="neural-network-viz"
          >
            <div style={{ color: '#0F0', fontSize: '12px', marginBottom: '10px', textAlign: 'center' }}>
              NEURAL NETWORK ACTIVE
            </div>
            {/* Neural nodes */}
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={i}
                className="neural-node"
                style={{
                  left: `${(i % 4) * 70 + 20}px`,
                  top: `${Math.floor(i / 4) * 60 + 40}px`,
                  animationDelay: `${i * 0.1}s`,
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Exit Hint */}
      <div className="matrix-exit-hint">
        Press ESC to exit Matrix Mode | Type "help" for commands
      </div>
    </motion.div>
  );
}

