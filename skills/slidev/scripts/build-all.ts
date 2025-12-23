#!/usr/bin/env bun
/**
 * Build all slide decks and generate a landing page index
 * 
 * Usage: bun run scripts/build-all.ts
 */

import { $ } from "bun";
import { readdir, readFile, mkdir, rm } from "node:fs/promises";
import { join, basename } from "node:path";
import { existsSync } from "node:fs";

interface DeckInfo {
  slug: string;
  title: string;
  description: string;
  file: string;
}

// Get repo name from package.json or git remote for base path
async function getRepoName(): Promise<string> {
  try {
    const pkg = await readFile("package.json", "utf-8");
    const { name, repository } = JSON.parse(pkg);
    
    // Try to extract from repository field
    if (repository?.url) {
      const match = repository.url.match(/github\.com[/:][\w-]+\/([\w-]+)/);
      if (match) return match[1];
    }
    
    // Fall back to package name
    if (name) return name.replace(/^@[\w-]+\//, "");
  } catch {
    // Ignore
  }
  
  // Try git remote
  try {
    const result = await $`git remote get-url origin`.text();
    const match = result.match(/github\.com[/:][\w-]+\/([\w-]+)/);
    if (match) return match[1].replace(/\.git$/, "");
  } catch {
    // Ignore
  }
  
  return "slides";
}

// Extract frontmatter from a slides file
async function extractFrontmatter(filePath: string): Promise<{ title: string; info: string }> {
  const content = await readFile(filePath, "utf-8");
  const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  
  let title = basename(filePath, ".slides.md");
  let info = "";
  
  if (frontmatterMatch) {
    const fm = frontmatterMatch[1];
    
    const titleMatch = fm.match(/^title:\s*(.+)$/m);
    if (titleMatch) title = titleMatch[1].replace(/^["']|["']$/g, "");
    
    const infoMatch = fm.match(/^info:\s*\|?\s*\n((?:\s{2,}.+\n?)*)/m);
    if (infoMatch) {
      info = infoMatch[1].replace(/^\s{2,}/gm, "").trim();
    } else {
      const singleInfo = fm.match(/^info:\s*(.+)$/m);
      if (singleInfo) info = singleInfo[1].replace(/^["']|["']$/g, "");
    }
  }
  
  return { title, info };
}

// Find all slide decks
async function findDecks(): Promise<DeckInfo[]> {
  const slidesDir = "slides";
  const decks: DeckInfo[] = [];
  
  if (!existsSync(slidesDir)) {
    console.error("No slides/ directory found");
    process.exit(1);
  }
  
  const files = await readdir(slidesDir);
  
  for (const file of files) {
    if (file.endsWith(".slides.md")) {
      const filePath = join(slidesDir, file);
      const { title, info } = await extractFrontmatter(filePath);
      const slug = basename(file, ".slides.md");
      
      decks.push({
        slug,
        title,
        description: info,
        file: filePath,
      });
    }
  }
  
  return decks.sort((a, b) => a.title.localeCompare(b.title));
}

// Generate landing page HTML
function generateLandingPage(decks: DeckInfo[], repoName: string): string {
  const deckCards = decks.map(deck => `
      <a href="/${repoName}/${deck.slug}/" class="deck-card">
        <h2>${escapeHtml(deck.title)}</h2>
        ${deck.description ? `<p>${escapeHtml(deck.description)}</p>` : ""}
        <span class="arrow">→</span>
      </a>`).join("\n");

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentations</title>
  <style>
    :root {
      --bg: #0f0f0f;
      --card-bg: #1a1a1a;
      --card-hover: #252525;
      --text: #e5e5e5;
      --text-muted: #888;
      --accent: #3b82f6;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      padding: 4rem 2rem;
    }
    
    .container {
      max-width: 900px;
      margin: 0 auto;
    }
    
    h1 {
      font-size: 2.5rem;
      margin-bottom: 0.5rem;
      font-weight: 600;
    }
    
    .subtitle {
      color: var(--text-muted);
      margin-bottom: 3rem;
      font-size: 1.1rem;
    }
    
    .deck-grid {
      display: grid;
      gap: 1rem;
    }
    
    .deck-card {
      display: block;
      background: var(--card-bg);
      border-radius: 12px;
      padding: 1.5rem 2rem;
      text-decoration: none;
      color: var(--text);
      transition: all 0.2s ease;
      position: relative;
      border: 1px solid transparent;
    }
    
    .deck-card:hover {
      background: var(--card-hover);
      border-color: var(--accent);
      transform: translateX(4px);
    }
    
    .deck-card h2 {
      font-size: 1.25rem;
      margin-bottom: 0.5rem;
      font-weight: 500;
    }
    
    .deck-card p {
      color: var(--text-muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }
    
    .deck-card .arrow {
      position: absolute;
      right: 1.5rem;
      top: 50%;
      transform: translateY(-50%);
      font-size: 1.5rem;
      color: var(--accent);
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    .deck-card:hover .arrow {
      opacity: 1;
    }
    
    .empty {
      text-align: center;
      color: var(--text-muted);
      padding: 4rem;
    }
    
    footer {
      margin-top: 4rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }
    
    footer a {
      color: var(--accent);
      text-decoration: none;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Presentations</h1>
    <p class="subtitle">${decks.length} slide deck${decks.length !== 1 ? "s" : ""} available</p>
    
    <div class="deck-grid">
      ${decks.length > 0 ? deckCards : '<p class="empty">No presentations yet</p>'}
    </div>
    
    <footer>
      Built with <a href="https://sli.dev" target="_blank" rel="noopener">Slidev</a>
    </footer>
  </div>
</body>
</html>`;
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// Main build process
async function main() {
  const repoName = await getRepoName();
  console.log(`📦 Building for repo: ${repoName}`);
  
  // Clean dist
  if (existsSync("dist")) {
    await rm("dist", { recursive: true });
  }
  await mkdir("dist", { recursive: true });
  
  // Find all decks
  const decks = await findDecks();
  console.log(`📑 Found ${decks.length} slide deck(s)`);
  
  // Build each deck
  for (const deck of decks) {
    console.log(`🔨 Building: ${deck.title} (${deck.file})`);
    const outDir = `dist/${deck.slug}`;
    const base = `/${repoName}/${deck.slug}/`;
    
    await $`bunx slidev build ${deck.file} --out ${outDir} --base ${base}`.quiet();
  }
  
  // Generate landing page
  console.log("🏠 Generating landing page...");
  const landingHtml = generateLandingPage(decks, repoName);
  await Bun.write("dist/index.html", landingHtml);
  
  // Create .nojekyll for GitHub Pages
  await Bun.write("dist/.nojekyll", "");
  
  console.log("✅ Build complete! Output in dist/");
}

main().catch(err => {
  console.error("Build failed:", err);
  process.exit(1);
});
