import path from 'path';
import util from 'util';
// eslint-disable-next-line import/no-extraneous-dependencies
import cors from 'cors';
import express from 'express';

import router from './routes';

const API_SERVER_PORT = 3030;

const app = express();

app.use(
  cors({
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    origin: ['http://localhost:6006', 'http://localhost:3003'],
  }),
);
app.use(express.json());

app.use(express.static(path.resolve(__dirname, '../../__mocks__/gzipped')));
app.use(express.static(path.resolve(__dirname, '../../public')));

app.use('/mock-data/api', (req, res, next) => {
  console.log(
    `[${req.method} ${req.path}] In mock data server: \n`,
    util.inspect({ reqBody: req.body }, { colors: true, depth: 1 }),
  );
  next();
});

app.use('/mock-data/api', router);

app.listen(API_SERVER_PORT, () => {
  console.log(`Mock Data App listening on port ${API_SERVER_PORT}...`);
  console.log('Press Ctrl+C to quit.');
});
