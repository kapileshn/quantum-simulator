@echo off
echo Starting Quantum Simulator...

:: Start the Python FastAPI backend in a new window
echo Starting backend server on port 8000...
start "Quantum Simulator - Backend" cmd /c "python api/simulation_api.py"

:: Wait a brief moment to ensure backend starts
timeout /t 2 /nobreak >nul

:: Start the React frontend in a new window
echo Starting frontend development server...
start "Quantum Simulator - Frontend" cmd /c "cd frontend && npm run dev"

:: Wait for Vite to boot up
timeout /t 3 /nobreak >nul

:: Open the browser
echo Opening simulator in default browser...
start http://localhost:5173

echo Done! The simulator is now running.
echo To stop, simply close the two command windows that were opened.
pause
