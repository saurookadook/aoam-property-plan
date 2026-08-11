import { Box, Paper } from '@mui/material';

import { FlexColumn, FlexRow } from '@/layouts';
import { TrendsRow } from './components';

import './styles.scss';

export function Home() {
  return (
    <FlexColumn id="home" className="home">
      <h2>{`🏡 Home 🏡`}</h2>

      <TrendsRow className="home__top-row" />

      <FlexRow style={{ width: '100%' }}>
        <Paper
          style={{
            height: '30rem',
            padding: '1rem',
            textAlign: 'center',
            width: '100%',
          }}
        >
          <Box
            style={{
              alignItems: 'center',
              border: '0.125rem dotted var(--mui-palette-primary-main)',
              display: 'flex',
              height: '100%',
              justifyContent: 'center',
              padding: '1rem',
              textAlign: 'center',
            }}
          >
            {`Maybe a graph or table?`}
          </Box>
        </Paper>
      </FlexRow>
    </FlexColumn>
  );
}
