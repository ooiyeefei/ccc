#!/usr/bin/env node
import { main } from "../scripts/daily-chief.mjs";

main().catch((error) => {
  const message = error instanceof Error && error.name === "DailyChiefError"
    ? error.message
    : "Daily Chief command failed. Check the command and try again.";
  process.stderr.write(`Error: ${message}\n`);
  process.exitCode = 1;
});
