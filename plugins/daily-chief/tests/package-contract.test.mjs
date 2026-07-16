import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import { fileURLToPath } from "node:url";

const skillPath = fileURLToPath(new URL("../skills/daily-chief/SKILL.md", import.meta.url));
const commandPath = fileURLToPath(new URL("../commands/daily-chief.md", import.meta.url));
const packagePath = fileURLToPath(new URL("../package.json", import.meta.url));

test("skill is user-invoked, Plan today only, and portable", async () => {
  const skill = await readFile(skillPath, "utf8");

  assert.match(skill, /^disable-model-invocation: true$/m);
  assert.match(skill, /# Daily Chief\n\nRemote truth\. Visual preview\. Explicit apply\./);
  assert.match(skill, /Only Plan today is implemented\./);
  assert.match(skill, /only after the command receives a successful remote response/i);
  assert.match(skill, /npx daily-chief-agent@1\.0\.0/);
  assert.doesNotMatch(skill, /\.pi\/skills\//);
  assert.doesNotMatch(skill, /\b(start[- ]work|check[- ]in|replan)\b/i);
});

test("Claude command is a strict user-invoked workflow loader", async () => {
  const command = await readFile(commandPath, "utf8");

  assert.match(command, /strict user-invoked command/i);
  assert.match(command, /skills\/daily-chief\/SKILL\.md/);
  assert.match(command, /Do not start Daily Chief work from generic product context/);
  assert.match(command, /explicit confirmation/);
});

test("package uses the public unscoped name and Pi skills manifest", async () => {
  const packageJson = JSON.parse(await readFile(packagePath, "utf8"));

  assert.equal(packageJson.name, "daily-chief-agent");
  assert.equal(packageJson.version, "1.0.0");
  assert.equal(packageJson.engines.node, ">=22");
  assert.equal(packageJson.bin["daily-chief"], "bin/daily-chief.mjs");
  assert.ok(packageJson.keywords.includes("pi-package"));
  assert.deepEqual(packageJson.pi, { skills: ["./skills"] });
});
