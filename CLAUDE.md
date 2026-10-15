# CLAUDE.md

# Software Engineering Guidelines

## 1. Core Objective

Build software that is: Correct, Simple, Secure, Maintainable, Performant, Testable, Consistent with the existing codebase.

The objective is not to produce the most code. The objective is to produce the best software with the least unnecessary complexity.

---

## 2. Critical Rule: Code Economy

Write the minimum amount of code necessary to implement the required behavior correctly, without sacrificing readability, correctness, security, testability, or maintainability. Before adding code, look for ways to reuse, simplify, or consolidate existing code, and remove unnecessary abstractions or obsolete code. Complexity must be justified by a real requirement.

---

## 3. Before Writing Code

1. Understand the requirement. 2. Inspect the relevant existing code. 3. Search the repository for existing implementations. 4. Identify existing patterns/conventions. 5. Check how related functionality currently works. 6. Determine the smallest reasonable change. 7. Consider edge cases and failure modes. 8. Only then modify the code.

---

## 4. Development Workflow

**Understand -> Inspect -> Plan -> Implement -> Verify -> Review -> Simplify**

- **Understand**: what needs to change, what must stay unchanged, what constraints exist.
- **Inspect**: search for existing components, functions, utilities, patterns, tests before creating anything new.
- **Plan**: for non-trivial changes, note files to modify, reusable code, simplest approach, risks.
- **Implement**: make the smallest safe change.
- **Verify**: run tests, type checking, linting, build, manual verification.
- **Review**: check the diff for unnecessary/unrelated changes, dead code, debug statements, security issues.
- **Simplify**: if it can be safely made simpler, simplify it.

---

## 5. DRY: Don't Repeat Yourself

Reuse existing functions/components, centralize shared constants, avoid duplicate implementations of the same behavior. Don't force unrelated code into an abstraction just to remove a few repeated lines; simple duplication can beat a bad abstraction.

---

## 6. KISS: Keep It Simple

Prefer simple, obvious solutions. Before introducing a new library, abstraction layer, design pattern, or state-management system, ask whether the existing architecture already solves the problem. Avoid clever code.

---

## 7. YAGNI: You Aren't Gonna Need It

Do not implement functionality that isn't currently required; no unused options, speculative APIs, hypothetical plugins, or unnecessary config. Implement what's needed now.

---

## 8. Existing Code First

Before creating something new, search the repository for similar functionality, reusable components, existing utilities, types, validation, error handling, styling, or patterns.

---

## 9. Architecture

Respect existing architecture unless there's a clear reason to change it. Prefer high cohesion, low coupling, clear boundaries, explicit dependencies, separation of concerns. Don't introduce a new pattern just because it's popular.

---

## 10. Avoid Overengineering

Don't build enterprise layering (Controller -> Service -> Repository -> Interface -> Adapter -> DTO -> Mapper) unless it solves an actual problem. Abstractions should exist for real value (reuse, isolation, testability, complexity management), not to demonstrate patterns.

---

## 11. SOLID

Apply where it improves the design, not mechanically:
- **SRP**: clear responsibility per module/function/class.
- **OCP**: extensible without constant modification of stable core logic, when it benefits the project.
- **LSP**: subtypes behave consistently with base-type contracts.
- **ISP**: don't force consumers to depend on unused functionality.
- **DIP**: depend on stable abstractions where useful, not unnecessary concretions.

---

## 12. Functions

Prefer small, focused functions. Avoid giant functions, excessive nesting/parameters, hidden side effects. Use early returns when they improve readability. Don't extract every few lines into a function just to make it "small."

---

## 13. Components and Modules

Avoid components that simultaneously fetch, transform, validate, and mutate data plus handle unrelated UI state. Separate responsibilities when it genuinely improves the design; don't over-split simple functionality.

---

## 14. Naming

Use descriptive names (`calculateInvoiceTotal()` not `calc()`; `customerId` not `id` when ambiguous). Avoid unnecessary abbreviations. Names should communicate intent.

---

## 15. Comments

Comments explain *why*, not *what*. Don't restate obvious code. Don't leave commented-out code; delete obsolete code.

---

## 16. Types

Use the type system properly: precise types, reuse existing types, avoid duplicate definitions, avoid `any` unless necessary, avoid unnecessarily complex generics.

---

## 17. Error Handling

Never silently swallow errors. Validate external input. Provide useful error messages and context. Handle expected failures; let unexpected failures surface appropriately. Don't wrap everything in unnecessary try/catch, and don't catch-and-ignore.

---

## 18. Security

Treat all external input as untrusted. Consider authN/authZ, input validation, output escaping, injection (SQL/XSS/CSRF/SSRF/path/command), sensitive data exposure, rate limiting, access control. Never hardcode secrets, commit credentials, expose API keys, trust client-side authorization, or disable security controls for convenience.

---

## 19. Database

Understand the existing schema before modifying it. Follow naming conventions, respect constraints, use transactions where atomicity matters, avoid unnecessary/N+1 queries, add indexes when justified, keep migrations safe, respect existing authorization/RLS policies.

---

## 20. APIs

Validate inputs and authorization. Return consistent responses with appropriate status codes. Avoid unnecessary API calls or breaking existing clients; preserve backwards compatibility when required. Don't create a new endpoint if an existing one can reasonably support the requirement.

---

## 21. Frontend

Reuse existing components, styles, and design tokens. Avoid duplicating UI logic; keep state local when practical, avoid unnecessary global state. Handle loading, error, empty, and success states. Consider responsive behavior and accessibility. Don't introduce a new UI library for one component without strong reason.

---

## 22. Dependencies

Before adding one: check if the project or language/framework already provides the functionality, consider a small local implementation, bundle size, maintenance cost, security, and licensing. Don't add a dependency for trivial functionality.

---

## 23. Performance

Measure before optimizing. Avoid unnecessary API requests, N+1 queries, repeated expensive calculations, unnecessary re-renders, oversized resources, inefficient algorithms. Don't sacrifice readability for negligible gains.

---

## 24. Testing

Test behavior, not implementation details. Prioritize critical business logic, important flows, edge/failure cases, security-sensitive behavior, regression prevention. Don't write meaningless tests just to raise coverage numbers.

---

## 25. Verification

Never assume code works because it looks correct. After changes: inspect the diff, run tests/type-checking/linting, build when appropriate, verify actual behavior. Don't stop after writing code.

---

## 26. Refactoring

Preserve existing behavior unless change is intentional. Reduce complexity, remove duplication/dead code/obsolete abstractions, keep the diff focused. Don't rewrite large parts of the project out of preference.

---

## 27. Scope Control

Stay within the requested scope. If asked to fix one thing, don't also rewrite unrelated architecture or components unless genuinely required. If you find an unrelated problem, mention it rather than silently expanding the task.

---

## 28. Preserve Existing Behavior

Before modifying shared code, determine where it's used, what depends on it, what callers assume, and whether tests cover it. Prefer backward-compatible changes.

---

## 29. Git Discipline

Keep changes focused: small logical commits, meaningful messages, clean diffs. Never commit secrets or unnecessary generated files, modify unrelated files, rewrite history without permission, or delete others' work. Inspect `git diff` / `git status` before finishing.

---

## 30. No Fake Completion

Never claim something is tested, working, fixed, deployed, or verified unless it actually was. State explicitly what was not verified. Never pretend a command succeeded if it wasn't run.

---

## 31. Ambiguous Requirements

Don't invent important requirements. If ambiguity materially affects implementation, ask for clarification. If minor, choose the simplest reasonable interpretation and proceed; don't block progress over trivial decisions.

---

## 32. Bad Existing Code

Don't automatically rewrite bad existing code. If it doesn't affect the current task, leave it (optionally mention it). If it directly affects the task, make the smallest necessary improvement; don't turn every task into a cleanup project.

---

## 33. Anti-Patterns

Avoid: overengineering, premature optimization/abstraction, excessive design patterns/comments/documentation/validation/error-handling/file-splitting/dependencies, giant functions/components, deep inheritance, duplicate implementations, dead/commented-out code, magic numbers, hardcoded secrets, speculative features, unnecessary config/state/API calls.

---

## 34. Code Reduction

After implementing, review for unnecessary complexity: removable code/abstractions, consolidatable helpers/files, avoidable dependencies, removable state/config. Remove what can go without reducing functionality, correctness, security, testability, or maintainability. Don't reduce code merely for line count.

---

## 35. Code Review Mindset

Review as if another engineer maintains it for years. Ask about correctness, simplicity, maintainability, security (can this be abused?), reliability (what if dependencies fail?), performance, testing, and scope (did this change anything unrelated?).

---

## 36. Decision Hierarchy

When choosing between implementations, prioritize in order: Correctness, Security, Simplicity, Readability, Maintainability, Reliability, Performance, Testability, Extensibility. Don't choose an approach merely because it's more sophisticated.

---

## 37. Practical 10-Second Check

Before finalizing: Am I duplicating existing code? Can this be simpler? Unnecessary abstraction/files/dependencies/complexity? Changed unrelated behavior? Handled important errors? Security issue? Actually tested? Inspected the diff?

---

## 38. Recommended Claude Code Workflow

For non-trivial tasks: Understand -> Inspect -> Plan -> Implement -> Verify -> Review -> Simplify -> **Report** (state what changed, what was tested, what was not tested, remaining concerns).

---

## 39. Useful Prompting Rules

- General: "Inspect the existing implementation first. Reuse existing patterns and make the smallest safe change. Do not refactor unrelated code."
- Bug fixes: "Find the root cause first. Fix it with the smallest change possible. Do not rewrite unrelated code."
- New features: "Inspect how similar functionality is already implemented. Follow the existing architecture instead of introducing a new pattern unless necessary."
- Cleanup: "Audit this area for unnecessary complexity, duplication, dead code, and redundant abstractions. Do not change behavior."
- Final verification: "Run the relevant tests, typecheck, lint, and build if applicable. Inspect the final diff and fix anything introduced by the changes."
- Code reduction: "Review the implementation for unnecessary code and abstraction. Simplify anything that can be safely removed while preserving functionality, correctness, security, and maintainability."

---

## 40. Final Principle

The best implementation is not the one with the most architecture, abstractions, or code.

Prefer: Simple > Clever · Necessary > Possible · Reuse > Duplicate · Explicit > Magical · Focused change > Rewrite · Measured optimization > Guessing · Existing pattern > New pattern · Minimum complexity > Maximum architecture · Working simplicity > Theoretical flexibility.

**The goal is maximum useful functionality with minimum unnecessary complexity.**
