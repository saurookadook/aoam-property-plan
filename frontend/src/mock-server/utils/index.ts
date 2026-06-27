import syncFs from 'fs';
import fs from 'fs/promises';
import path from 'path';
import { pipeline } from 'stream/promises';
import { promisify } from 'util';
import zlib from 'zlib';

import type { KeyedObject } from '@src/types';

export function createPathFileFromComponent(dateStr?: string) {
  if (dateStr == null) {
    return '';
  }

  return dateStr.replace(/\s/g, '_').replace(/:/g, '-');
}

export function buildBasePathToGzippedData({
  endTimeParam,
  filename,
  startTimeParam,
  entityId,
  entityType,
}: {
  endTimeParam?: string;
  filename: string;
  startTimeParam?: string;
  entityId: string;
  entityType: string;
}) {
  return path.join(
    '__mocks__',
    'gzipped',
    createPathFileFromComponent(startTimeParam),
    createPathFileFromComponent(endTimeParam),
    filename,
  );
}

/** @note Should resolve to `frontend` */
const baseDir = path.resolve();

export async function readGzippedJsonInChunks(filePath: string): Promise<KeyedObject> {
  const chunks: any[] = [];
  const collector = async function* (source: any) {
    for await (const chunk of source) {
      chunks.push(chunk);
      yield;
    }
  };

  await pipeline(
    syncFs.createReadStream(filePath), // force formatting
    zlib.createGunzip(),
    collector,
  );

  return JSON.parse(Buffer.concat(chunks).toString('utf-8'));
}

const gunzip = promisify(zlib.gunzip);

export async function readGzippedJson(filePath: string): Promise<KeyedObject> {
  const resolvedPath = path.resolve(baseDir, filePath);
  const fileBuffer = await fs.readFile(resolvedPath);
  const jsonBuffer = await gunzip(fileBuffer);
  return JSON.parse(jsonBuffer.toString('utf-8'));
}
