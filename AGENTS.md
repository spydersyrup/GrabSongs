# Engineering Rules for AI Coding Agents

These rules apply to every coding agent working on this repository.

The goal is not to generate as much code as possible.

The goal is to make the **smallest correct change**, preserve the existing architecture, keep the repository easy to understand, and leave the code in a state that an experienced engineer would be comfortable maintaining.

Treat this as a mature open-source project.

---

# 1. Core Engineering Philosophy

Always optimize for:

* correctness
* simplicity
* readability
* maintainability
* consistency
* security
* performance where relevant
* reuse
* small diffs
* predictable behavior

Do not optimize for:

* number of lines written
* cleverness
* novelty
* abstraction for its own sake
* showing off patterns
* unnecessary flexibility
* speculative future requirements

A good change often removes code instead of adding code.

Prefer:

```text
simple > clever
existing > new
explicit > magical
small > large
readable > compact tricks
boring and reliable > impressive
```

---

# 2. Understand the Codebase Before Editing

Before changing anything:

1. Inspect the relevant directory.
2. Find the existing implementation.
3. Search for similar functionality.
4. Search for existing components.
5. Search for existing utilities.
6. Search for existing hooks/services/helpers.
7. Search for existing constants.
8. Search for existing models/types/interfaces.
9. Check how similar features are implemented elsewhere.
10. Understand the project's architecture and conventions.

Never immediately create a new file because something appears missing.

First determine whether the functionality already exists somewhere else.

Do not implement something twice because you failed to search properly.

---

# 3. Preserve Existing Architecture

Follow the architecture already used by the project.

Do not introduce a new architectural pattern unless there is a clear technical reason.

For example, do not suddenly introduce:

* repositories
* service layers
* use-case layers
* dependency injection frameworks
* state management libraries
* event buses
* factories
* adapters
* command patterns
* mediator patterns

when the existing project does not use them.

Consistency with the existing codebase is usually more valuable than theoretical architectural purity.

---

# 4. Minimal Changes

Modify the minimum amount of code necessary to complete the task.

Do not refactor unrelated files.

Do not rename unrelated variables.

Do not reformat entire files because you changed five lines.

Do not reorganize folders unless the task requires it.

Do not modify working code simply because you personally prefer another implementation.

Avoid large diffs when a small diff solves the problem.

Every changed line should have a reason.

---

# 5. No Useless Code

Do not generate code that does not provide immediate value.

Never add:

* unused functions
* unused variables
* unused imports
* unused parameters
* unused components
* unused interfaces
* unused classes
* unused configuration
* unused feature flags
* placeholder implementations
* speculative helpers
* dead branches
* unreachable code
* commented-out code

Delete obsolete code instead of leaving it around.

The repository is not an archive.

Git already preserves history.

---

# 6. Avoid Duplication

Before writing new logic, search for existing logic that already does the same thing.

Reuse existing:

* components
* functions
* utilities
* hooks
* services
* models
* schemas
* constants
* themes
* styles
* validators
* API clients
* error handlers
* formatters
* parsers
* layouts

Do not copy-paste an existing implementation and slightly modify it.

If two implementations genuinely share behavior, extract the shared behavior at the correct level.

However, do not blindly apply DRY.

Two pieces of code that merely look similar are not necessarily the same abstraction.

Avoid premature abstraction.

---

# 7. Prefer Existing Components

For UI work, search the component library before creating anything new.

If the repository already has:

```text
Button
Card
Dialog
Modal
Input
Select
Dropdown
Tabs
Tooltip
Badge
Avatar
Loader
EmptyState
ErrorState
PageHeader
SectionHeader
```

reuse them.

Do not create:

```text
NewButton
CustomButton
BetterButton
Button2
ModernCard
FancyCard
SpecialDialog
```

unless the new component genuinely represents different reusable behavior.

Extend an existing component when appropriate.

---

# 8. Do Not Create Files Unnecessarily

New files introduce maintenance cost.

Before creating a file, determine whether the code belongs naturally in an existing file.

Do not create files such as:

```text
helpers.ts
utils2.ts
commonUtils.ts
misc.ts
sharedHelpers.ts
constants2.ts
newTypes.ts
temp.ts
```

without a clear responsibility.

File names should communicate what the file owns.

Split files by responsibility, not arbitrary line-count rules.

A long cohesive file can be better than ten tiny files that require constant navigation.

---

# 9. Avoid Over-Abstraction

Do not create an abstraction for a single use case unless it meaningfully improves clarity.

Avoid unnecessary:

* wrappers
* interfaces
* factories
* providers
* adapters
* base classes
* generic managers
* generic repositories
* generic services
* configuration layers

Bad:

```text
Button
→ ButtonProvider
→ ButtonManager
→ ButtonFactory
→ ButtonRenderer
→ Actual Button
```

Prefer direct implementations when the problem is simple.

An abstraction should remove meaningful complexity, not relocate it.

---

# 10. Avoid Premature Generalization

Implement the requirements that exist now.

Do not build imaginary future features.

Avoid comments or abstractions such as:

```text
// In case we need multiple providers later...
// Future support for...
// This allows us to eventually...
```

unless those requirements already exist.

Do not turn a simple implementation into a generic framework.

---

# 11. Keep Code Compact Without Making It Cryptic

Prefer concise implementations when they remain readable.

Remove:

* repetitive branches
* redundant intermediate variables
* unnecessary transformations
* duplicated conditions
* unnecessary wrappers
* unnecessary indirection

But never reduce code merely to minimize line count.

Readable:

```text
small and obvious
```

is better than:

```text
short and clever
```

The target is high information density, not code golf.

---

# 12. Functions Should Have Clear Responsibilities

Functions should generally do one coherent thing.

Avoid functions that:

* fetch data
* transform data
* update UI
* write storage
* log events
* handle navigation

all at once.

Extract responsibilities when doing so genuinely improves understanding.

Do not split every five-line function into another five-line function.

Use judgment.

---

# 13. Naming Must Be Precise

Names should describe intent.

Prefer:

```text
loadUserProfile()
calculateInvoiceTotal()
isSessionExpired
formattedDuration
activePlaylist
```

Avoid:

```text
doThing()
handleStuff()
processData()
temp()
helper()
manager()
data2
valueX
foo
bar
```

Do not add words such as:

```text
Manager
Processor
Handler
Service
Helper
Util
Controller
```

unless the object actually performs that responsibility.

---

# 14. Avoid Redundant Naming

Context already provides information.

Bad:

```text
User.userName
Playlist.playlistSongs
Invoice.invoiceTotalAmount
```

Better:

```text
User.name
Playlist.songs
Invoice.total
```

Avoid unnecessarily verbose identifiers.

---

# 15. Comments Should Explain Why

Do not narrate obvious code.

Bad:

```js
// Increment count
count++;

// Check if user exists
if (user) {
```

These comments add noise.

Use comments for:

* non-obvious constraints
* architectural reasoning
* compatibility issues
* external API quirks
* security assumptions
* unusual algorithms
* decisions that would otherwise look incorrect

A useful comment explains **why**, not **what**.

---

# 16. No AI-Style Comments

Never add verbose generated comments such as:

```text
// This function is responsible for handling the user's request
// Here we initialize the variable
// Now we iterate through the array
// This ensures optimal performance
// This provides a robust solution
// This improves maintainability and scalability
```

Avoid section comments everywhere such as:

```text
// ===========================
// DATA PROCESSING SECTION
// ===========================
```

unless the existing repository consistently uses them.

The code itself should communicate structure.

---

# 17. Do Not Leave Meta Commentary

Never write comments mentioning:

* AI
* ChatGPT
* Claude
* Gemini
* coding agents
* generated code
* prompts
* user requests

For example, never write:

```text
// Added based on user request
// AI-generated fallback
// Claude suggested this implementation
```

Repository code should stand independently.

---

# 18. No Fake Documentation

Do not add large documentation blocks for trivial functions.

Avoid:

```text
/**
 * This function gets the user's name.
 *
 * @param user The user object containing...
 * @returns The user's name...
 */
```

for:

```js
const getName = user => user.name;
```

Documentation should add information that cannot easily be inferred from the code.

---

# 19. Error Handling Must Be Meaningful

Do not wrap everything in `try/catch`.

Bad:

```js
try {
  ...
} catch (error) {
  console.log(error);
}
```

Handle an error only when you can:

* recover
* retry
* translate it
* provide useful context
* show appropriate UI
* clean up resources
* intentionally propagate it

Never silently swallow failures.

---

# 20. Do Not Hide Bugs With Fallbacks

Do not solve unexpected states by blindly returning defaults.

Examples:

```js
return []
return {}
return null
return false
```

may hide genuine bugs.

Fallback behavior should be intentional and documented through code structure.

Unexpected states should fail clearly when appropriate.

---

# 21. Avoid Excessive Defensive Programming

Do not repeatedly check impossible conditions simply because an AI agent wants the code to look "safe."

If upstream validation guarantees something, trust the contract unless there is evidence that the contract is unreliable.

Avoid layers of redundant:

```text
null checks
undefined checks
empty checks
type checks
fallback checks
```

that obscure the actual logic.

Defensive programming should address realistic failure modes.

---

# 22. Respect Type Systems

Do not bypass type safety to make errors disappear.

Avoid:

```text
any
dynamic
Object
unknown casts
force unwraps
unchecked casts
eslint-disable
ts-ignore
```

unless genuinely necessary.

Never solve a type error by weakening the entire type system.

Fix the actual type relationship.

---

# 23. Avoid Duplicate Types

Search for existing types before introducing new ones.

Do not create:

```text
User
UserData
UserInfo
UserModel
UserDetails
UserObject
```

representing effectively the same entity.

Prefer one canonical representation where practical.

---

# 24. Constants Should Be Centralized Appropriately

Do not scatter magic values throughout the application.

But also do not create a constant for every literal.

Useful constants represent:

* domain rules
* configuration
* repeated values
* meaningful thresholds

Avoid pointless constants like:

```js
const ONE = 1;
const EMPTY_STRING = "";
```

---

# 25. Dependencies Require Justification

Do not install a package for functionality that can be implemented clearly in a few lines.

Before adding a dependency:

1. Check whether the project already has something equivalent.
2. Check whether the platform provides the functionality.
3. Consider maintenance cost.
4. Consider package size.
5. Consider security implications.
6. Consider license compatibility.
7. Consider whether the dependency is actively maintained.

Every dependency becomes part of the project's long-term maintenance surface.

---

# 26. Do Not Replace Existing Libraries Without Reason

If the project already uses a library successfully, use it.

Do not introduce a second library that performs the same job.

Examples:

```text
two HTTP clients
two date libraries
two icon libraries
two state managers
two validation frameworks
```

should generally be avoided.

---

# 27. UI Must Follow the Existing Design Language

Before creating UI:

* inspect existing screens
* inspect spacing
* inspect typography
* inspect colors
* inspect components
* inspect interaction patterns
* inspect responsive behavior

New screens should feel like they belong to the same application.

Do not redesign the application while implementing one feature.

---

# 28. No AI-Slop UI

Do not automatically add visual effects because they appear "modern."

Avoid unnecessary:

* gradients
* glows
* neon borders
* blurred blobs
* glassmorphism
* huge shadows
* excessive cards
* excessive rounded containers
* floating decorative shapes
* gradient text
* animated gradients
* glowing icons
* random illustrations
* decorative background noise
* giant hero text
* excessive badges
* pill-shaped everything

Do not turn every piece of information into a card.

Do not put cards inside cards inside cards.

Use visual hierarchy instead of decoration.

---

# 29. UI Should Be Restrained

Prefer:

* clean spacing
* strong typography
* alignment
* sensible contrast
* clear hierarchy
* consistent components
* predictable interactions

A professional interface should not need decorative effects to look polished.

Use whitespace intentionally.

---

# 30. Avoid Excessive Rounded Corners

Do not default everything to extremely large corner radii.

Buttons, dialogs, cards, inputs and containers should follow the existing design system.

Do not make every UI element pill-shaped.

---

# 31. Avoid Unnecessary Animations

Animation should communicate:

* state change
* hierarchy
* navigation
* feedback
* spatial relationship

Do not add animation simply to make the interface feel impressive.

Avoid:

* constant floating
* pulsing
* glowing
* bouncing
* rotating decoration

Respect reduced-motion preferences where applicable.

---

# 32. Do Not Invent UX

Do not introduce:

* additional dialogs
* confirmations
* onboarding screens
* tooltips
* popups
* notifications
* banners

unless they serve a genuine user need.

Every interaction creates friction.

---

# 33. Accessibility Is Part of Correctness

Consider:

* keyboard navigation
* focus states
* semantic controls
* screen readers
* sufficient contrast
* readable font sizes
* touch target sizes
* reduced motion
* form labels
* error descriptions

Do not sacrifice accessibility for appearance.

---

# 34. Avoid Hardcoded Layout Hacks

Do not fix layout issues with arbitrary values until understanding the underlying layout system.

Avoid excessive:

```text
margin-left: 17px
top: -3px
transform: translate(...)
absolute positioning
z-index: 999999
```

unless technically justified.

Prefer layout systems over positional hacks.

---

# 35. Security Is Not Optional

Never expose:

* secrets
* API keys
* tokens
* credentials
* private keys
* internal endpoints
* user-sensitive information

Do not commit secrets even temporarily.

Validate external input at trust boundaries.

Use established security primitives.

Never implement custom cryptography.

---

# 36. Do Not Trust Client Input

For client/server systems:

Client-side validation improves UX.

Server-side validation provides security.

Authorization must be enforced server-side.

Do not rely on hidden buttons or frontend state for access control.

---

# 37. Database Changes Must Be Safe

For database work:

* preserve existing data
* understand existing schema
* check constraints
* check indexes
* avoid destructive migrations
* make migrations deterministic
* consider rollback implications
* maintain tenant isolation where relevant

Do not casually rename or delete columns in production systems.

---

# 38. Avoid N+1 Work

Watch for unnecessary repeated:

* network requests
* database queries
* filesystem reads
* expensive calculations
* rendering

Prefer batching or caching where justified.

Do not add caching without understanding invalidation.

---

# 39. Performance Optimization Must Be Evidence-Based

Do not complicate code for theoretical performance improvements.

Optimize when:

* there is measurable impact
* the operation is known to be expensive
* the scale requires it
* profiling identifies it

Do not introduce complexity based on assumptions.

---

# 40. State Must Have a Clear Owner

Avoid multiple competing sources of truth.

Determine which layer owns each piece of state.

Do not duplicate the same state across:

* component state
* global state
* database state
* caches
* service state

unless synchronization behavior is clearly defined.

---

# 41. Keep Data Flow Predictable

Prefer understandable data flow.

Avoid invisible mutation.

Avoid excessive global state.

Avoid side effects hidden inside unrelated functions.

A maintainer should be able to follow:

```text
input
→ transformation
→ state change
→ output
```

without tracing ten abstractions.

---

# 42. APIs Must Have Clear Contracts

When modifying APIs:

* preserve compatibility where required
* validate input
* define expected output
* handle meaningful failure cases
* avoid inconsistent response structures

Do not silently change existing API behavior.

---

# 43. Logging Must Be Useful

Do not flood the application with logs.

Avoid logs such as:

```text
function called
button clicked
entered loop
data received
```

unless needed for actual diagnostics.

Never log sensitive information.

Use existing logging infrastructure.

Remove temporary debugging logs before completing the task.

---

# 44. Tests Must Test Behavior

Do not create tests merely to increase test count.

Avoid tests that only confirm mocks behave as configured.

Prefer testing:

* public behavior
* domain rules
* regressions
* important edge cases
* failure paths

Do not rewrite implementation purely to satisfy poorly designed tests.

---

# 45. Do Not Mock Everything

Excessive mocking creates tests disconnected from reality.

Mock actual external boundaries when needed.

Prefer real internal logic.

Tests should provide confidence, not ceremony.

---

# 46. Fix Root Causes

Do not patch symptoms.

When fixing a bug:

1. Identify why it happens.
2. Find the source of incorrect state or behavior.
3. Correct the root cause.
4. Check other paths affected by the same assumption.
5. Add a regression test when practical.

Avoid chains of special-case conditions.

---

# 47. Do Not Stack Patches

If previous fixes created:

```text
if specialCase1
if specialCase2
if specialCase3
```

investigate whether the underlying model is wrong.

Three patches around the same behavior usually indicate a deeper problem.

---

# 48. Refactor Only With Purpose

Good reasons to refactor include:

* duplicated logic
* unclear responsibility
* unsafe code
* difficult testing
* bug-prone architecture
* significant maintenance friction

Bad reason:

```text
"I think this looks cleaner."
```

Do not refactor unrelated areas while delivering a feature.

---

# 49. Delete Complexity When Possible

When modifying existing code, consider whether functionality can be simplified.

Prefer removing:

* obsolete compatibility layers
* unnecessary wrappers
* duplicated state
* redundant transformations
* dead configuration
* obsolete feature flags

A smaller system is generally easier to maintain.

---

# 50. Git Changes Should Be Reviewable

Changes should be logically grouped.

Do not mix:

```text
feature implementation
formatting
renaming
dependency updates
folder restructuring
unrelated refactors
```

into one change.

A maintainer should quickly understand what changed and why.

---

# 51. Do Not Touch Generated Files Manually

Identify generated files before modifying them.

Examples may include:

* lock-generated artifacts
* generated API clients
* build files
* generated schemas
* compiled output

Modify the source and regenerate properly when appropriate.

---

# 52. Respect Formatting and Linting

Use the project's existing:

* formatter
* linter
* naming conventions
* import ordering
* style rules

Do not introduce personal formatting preferences.

Do not disable lint rules simply to make warnings disappear.

---

# 53. Avoid Formatting Noise

Do not reformat unrelated lines.

Large formatting diffs hide meaningful code changes and make reviews harder.

---

# 54. Open-Source Maintainability

Assume another developer will encounter your code six months later without context.

They should be able to understand:

* where functionality lives
* why it exists
* how data flows
* how errors are handled
* how to modify it safely

Avoid architecture that only makes sense to the agent that created it.

---

# 55. Keep Public APIs Small

Do not export everything.

Keep implementation details private.

Expose only what other parts of the application genuinely need.

A smaller public surface makes refactoring easier.

---

# 56. Avoid Utility Dumping Grounds

Do not put unrelated functions into large generic utility files.

Prefer domain-specific locations.

Bad:

```text
utils.ts
  formatMoney
  parsePlaylist
  validateEmail
  calculateTax
  resizeImage
  retryRequest
```

Better organization groups behavior by ownership and domain.

---

# 57. Avoid Giant "God" Objects

Watch for:

```text
AppManager
GlobalService
ApplicationController
CommonUtils
EverythingProvider
```

that become responsible for unrelated functionality.

Split responsibilities when boundaries become clear.

---

# 58. Avoid Excessive Micro-Files

The opposite problem is also harmful.

Do not create:

```text
one function per file
one interface per file
one constant per file
```

without a meaningful organizational reason.

Navigation cost matters.

Keep closely related code together.

---

# 59. Respect Existing Domain Language

Use terminology already established by the project.

Do not rename domain concepts casually.

Consistent vocabulary makes a codebase easier to understand.

---

# 60. Avoid Clever Language Tricks

Do not use obscure language features merely to reduce lines.

Prefer code that an experienced developer can scan quickly.

Avoid unnecessary:

* metaprogramming
* reflection
* nested ternaries
* deeply chained expressions
* operator tricks
* implicit conversions

Explicit code is often easier to maintain.

---

# 61. Control Nesting

Deep nesting makes logic difficult to follow.

Prefer:

* early returns
* guard clauses
* extracted meaningful functions

where they improve clarity.

Avoid deeply nested:

```text
if
  if
    if
      for
        if
```

structures.

---

# 62. Handle Edge Cases Proportionally

Consider realistic edge cases.

Do not invent dozens of theoretical scenarios that dramatically complicate otherwise simple code.

Prioritize:

* expected failures
* known platform behavior
* real input boundaries
* user-controlled data
* network failure
* persistence failure

---

# 63. Do Not Add TODOs Casually

Do not leave:

```text
TODO
FIXME
HACK
TEMP
```

unless there is a clear reason they must remain.

If the issue can reasonably be fixed while working on the task, fix it.

Do not use TODOs to avoid completing necessary work.

---

# 64. Avoid Fake Robustness

AI-generated code often appears "robust" because it includes excessive layers.

More code does not mean more reliability.

Reliability comes from:

* clear contracts
* simple state
* correct validation
* appropriate error handling
* meaningful tests
* limited responsibility

---

# 65. Avoid Boilerplate

Do not produce repetitive ceremony simply because a framework tutorial commonly uses it.

Use the least amount of framework machinery necessary.

---

# 66. Do Not Rewrite Working Systems

Never replace a functioning subsystem with a new implementation unless the task specifically requires it or there is a demonstrated technical issue.

Existing battle-tested code has value.

---

# 67. Preserve Backwards Compatibility

Before changing existing behavior, identify consumers.

Consider:

* public APIs
* stored data
* configuration
* URLs
* deep links
* serialized formats
* database records
* external integrations

Do not break existing users unnecessarily.

---

# 68. Maintain Platform Conventions

Follow established conventions for the platform.

For example:

* Android should behave like Android.
* Desktop applications should follow desktop interaction expectations.
* Web applications should respect browser semantics.
* CLI applications should follow common CLI behavior.

Do not reinvent fundamental platform behavior.

---

# 69. No Fake Data in Production Paths

Do not silently insert:

* placeholder users
* sample responses
* fake products
* mock API results
* hardcoded demo values

into production flows.

Mock data belongs in clearly separated development or testing environments.

---

# 70. Do Not Hide Missing Implementations

If something cannot be implemented correctly because required infrastructure is absent, make the limitation explicit.

Do not create a fake implementation that appears functional.

---

# 71. Preserve User Data

Never introduce operations that can unexpectedly destroy or overwrite user data.

For destructive actions:

* confirm intention where appropriate
* make scope clear
* use transactions when necessary
* support recovery where practical

---

# 72. Respect Concurrency

When code is asynchronous or concurrent, understand:

* ownership
* cancellation
* race conditions
* lifecycle
* retries
* duplicate execution

Do not fix concurrency bugs with arbitrary delays.

Never use:

```text
sleep(500)
delay(1000)
setTimeout(...)
```

as a synchronization mechanism unless the delay itself is a product requirement.

---

# 73. Retry Carefully

Do not blindly retry failures.

Retries should generally be used only for transient failures.

Consider:

* exponential backoff
* retry limits
* idempotency
* cancellation
* rate limits

Never create infinite retry loops.

---

# 74. Keep Configuration Clear

Configuration should have one obvious source.

Avoid duplicating configuration across several files.

Environment-specific configuration should remain environment-specific.

Do not hardcode production values into application logic.

---

# 75. Respect Licenses

For an open-source repository:

* do not copy incompatible licensed code
* preserve required notices
* check dependency licensing
* attribute external code where legally required

Do not copy large snippets from random repositories without understanding their license.

---

# 76. Do Not Add Unnecessary README Noise

Documentation should describe useful information.

Do not turn the README into marketing fluff.

Avoid excessive:

* badges
* slogans
* generated feature descriptions
* emoji-heavy sections
* redundant explanations

unless they match the repository's existing style.

---

# 77. Keep Documentation Synchronized

If behavior that users or contributors rely upon changes, update the relevant documentation.

Do not document implementation details that are likely to become stale unnecessarily.

---

# 78. Do Not Change Dependency Versions Casually

Do not upgrade packages simply because newer versions exist while implementing an unrelated task.

Dependency upgrades can introduce unrelated regressions.

Keep them separate unless required.

---

# 79. Verify Before Declaring Completion

Before finishing:

* inspect the final diff
* remove unused code
* remove debug code
* remove temporary files
* check imports
* run formatting
* run linting
* run relevant tests
* run type checking
* build the affected target when practical

Do not assume code works because it looks correct.

---

# 80. Review Your Own Diff

Before presenting the result, read the diff as if reviewing someone else's pull request.

Ask:

* Did I change anything unrelated?
* Did I duplicate existing functionality?
* Did I add unnecessary files?
* Did I add unnecessary abstractions?
* Could this implementation be simpler?
* Did I accidentally weaken type safety?
* Did I introduce hidden behavior?
* Are names understandable?
* Are comments actually useful?
* Did I leave debugging code?
* Does the UI match the existing application?
* Would a maintainer understand this six months later?

If the answer reveals unnecessary complexity, simplify before finishing.

---

# 81. Agent-Specific Anti-Patterns

Coding agents frequently produce certain patterns that should be actively avoided.

Do not:

* create unnecessary helper functions
* create unnecessary interfaces
* introduce abstractions after only one use
* over-comment obvious code
* add excessive error handling
* add speculative fallback behavior
* create duplicate components
* recreate existing utilities
* add dependencies unnecessarily
* create giant configuration systems
* create excessive test mocks
* generate placeholder documentation
* create unnecessary wrapper classes
* add "future-proofing" architecture
* rename unrelated code
* reformat unrelated files
* rewrite working functionality
* add gradients or glows to make UI "modern"
* produce generic dashboard-style interfaces
* create cards for every section
* add animations without UX justification
* insert decorative UI elements
* generate enormous files when a small modification works
* split code into dozens of files without reason
* add compatibility layers for hypothetical requirements

---

# 82. Senior Engineer Decision Rule

When multiple solutions are possible, choose the one an experienced maintainer would likely choose:

1. Understand the existing system.
2. Reuse what already works.
3. Modify the smallest surface possible.
4. Keep behavior explicit.
5. Avoid introducing new concepts.
6. Preserve compatibility.
7. Handle realistic failures.
8. Verify the result.
9. Leave the code simpler or equally understandable as before.

Do not treat every task as an opportunity to redesign the system.

---

# 83. Ask "Can This Be Deleted?"

Whenever adding code, consider whether existing code can instead be:

* reused
* simplified
* consolidated
* removed

Net-negative code changes can be excellent engineering.

Example:

```text
+20 lines
-80 lines
```

may be better than:

```text
+300 lines
-0 lines
```

if both solve the same problem correctly.

---

# 84. Avoid Line-Count Obsession

Smaller codebases are generally easier to understand, but raw line count is not the objective.

Do not compress readable code simply to reduce LOC.

The real objective is reducing:

* duplication
* unnecessary abstraction
* unnecessary state
* boilerplate
* dead code
* cognitive overhead

Measure complexity, not just lines.

---

# 85. Locality Matters

Keep logic close to where it is used unless sharing it provides meaningful benefit.

Do not move every small piece of logic into a global utility.

Developers should not need to jump through six files to understand a ten-line feature.

---

# 86. Prefer Composition Over Special Cases

When multiple variants exist, use the project's established composition mechanisms rather than copying entire components and changing a few lines.

But do not build an overly generic configurable component with dozens of boolean properties.

Bad:

```text
<Component
  isCompact
  isLarge
  isSpecial
  useAlternateHeader
  enableNewMode
  legacyMode
/>
```

At that point, responsibilities should probably be reconsidered.

---

# 87. Boolean Parameters Require Care

Calls such as:

```text
createUser(true, false, true)
```

are difficult to understand.

Prefer descriptive parameters or clearer APIs where appropriate.

---

# 88. Avoid Temporal Coupling

Code should not depend on unrelated functions being called in an undocumented specific order.

If ordering matters, make the relationship explicit through structure or API design.

---

# 89. Avoid Hidden Side Effects

Functions named like queries should not unexpectedly mutate global state.

For example:

```text
getUser()
```

should not unexpectedly delete cache entries or update unrelated settings.

Names and behavior should agree.

---

# 90. Keep Business Logic Out of Presentation Code

Where the architecture supports separation, keep domain rules separate from UI rendering.

UI components should not become containers for unrelated business rules.

Likewise, do not introduce unnecessary architecture for trivial display transformations.

Use proportional judgment.

---

# 91. Design System Rules

When a design system exists, use its:

* spacing scale
* typography
* colors
* radii
* shadows
* icons
* motion
* components

Do not introduce visually similar but slightly different values.

Avoid design drift.

---

# 92. Icons

Use the project's existing icon library.

Do not mix multiple icon sets without a strong reason.

Do not substitute arbitrary emoji for interface icons.

Use icons only when they improve recognition or hierarchy.

---

# 93. Forms

Forms should provide:

* proper labels
* clear validation
* practical error messages
* predictable submission state
* disabled/loading states where appropriate

Do not clear user input after an unrelated failure.

Do not allow duplicate submissions accidentally.

---

# 94. Loading States

Do not introduce loading spinners everywhere.

Prefer the loading treatment already established by the application.

Avoid fake loading delays.

Never intentionally delay a fast operation just to display animation.

---

# 95. Empty States

Empty states should explain the actual state and, where useful, provide the obvious next action.

Avoid generic copy such as:

```text
Nothing here yet!
Start your amazing journey today.
```

Use concise product-specific language.

---

# 96. Error Messages

Error messages should help the user understand what happened and what they can do.

Avoid exposing:

* stack traces
* database errors
* internal implementation details
* raw exception messages

in production UI.

Likewise, avoid vague messages when a meaningful error is known.

---

# 97. Human-Written Code Standard

The repository should not look machine-generated.

Code should feel deliberate.

Each abstraction should have a reason.

Each file should have a clear purpose.

Each component should belong.

Each comment should communicate useful context.

Each dependency should justify its existence.

Each error handler should address a real failure.

Each UI element should serve a function.

Nothing should exist simply because generating it was easy.

---

# 98. When Unsure

When uncertain between:

```text
adding more architecture
```

and:

```text
using the existing simple implementation
```

prefer the existing simple implementation.

When uncertain between:

```text
creating something new
```

and:

```text
reusing something existing
```

inspect the repository and reuse where appropriate.

When uncertain between:

```text
a clever implementation
```

and:

```text
an obvious implementation
```

choose the obvious one.

---

# 99. Definition of Done

A task is complete only when:

* the requested behavior works
* existing behavior remains intact
* no unnecessary code was introduced
* no duplicate implementation was introduced
* existing components were reused where appropriate
* architecture remains consistent
* types remain sound
* realistic errors are handled
* temporary code is removed
* UI matches the existing design language
* accessibility has not regressed
* relevant tests pass
* linting/type checks pass
* the affected target builds when applicable
* the final diff contains only intentional changes
* documentation is updated when necessary

---

# 100. Final Rule

Do not behave like a code generator.

Behave like a senior engineer maintaining a codebase they expect to work on for the next ten years.

Understand first.

Reuse second.

Change only what is necessary.

Simplify whenever possible.

Verify everything.

Leave the repository cleaner, clearer, and no more complicated than it needs to be.
