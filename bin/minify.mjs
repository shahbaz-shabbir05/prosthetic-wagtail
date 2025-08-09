import fs from 'fs';
import path from 'path';
import { Command } from 'commander';
import { minify } from 'html-minifier-terser';
import { glob, readFile, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const program = new Command();

program.argument('<path>', 'Path to look for HTML files.').action((path) => {
  const globexpr = join(path, '**/*.html');
  glob(globexpr, parseFiles);
});

program.parse();

function parseFiles(err, filePaths) {
  for (const filePath of filePaths) {
    readFile(filePath, 'utf-8', async (err, data) => {
      const result = await minify(data, {
        collapseWhitespace: true,
        minifyJS: true,
        minifyCSS: true,
      });

      writeFileSync(filePath, result);
    });
  }
}
