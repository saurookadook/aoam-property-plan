import { RouterProvider } from 'react-router';

import browserRouter from '@/app/browserRouter';
import './App.scss';

function App() {
  return (
    <main>
      <RouterProvider router={browserRouter} />
    </main>
  );
}

export default App;
