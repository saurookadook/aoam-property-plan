import { useState } from 'react';

export function Home() {
  const [count, setCount] = useState(0);

  function handleCounterClick(
    event: React.MouseEvent<HTMLButtonElement>, // force formatting
  ) {
    const newCount = count + 1;
    setCount(newCount);
  }

  return (
    <div id="home">
      <h2>{`🏡 Home 🏡`}</h2>

      <button // force formatting
        onClick={handleCounterClick}
      >
        count is {count}
      </button>
    </div>
  );
}
