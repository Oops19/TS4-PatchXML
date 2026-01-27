# 🧬 Important Limitations & Recommendations
Trait affordances and some tests are compiled once during game startup.
* [Live XML](https://github.com/Oops19/TS4-LiveXML) cannot be used to add or modify trait affordances and/or various tests
* [Patch XML](https://github.com/Oops19/TS4-PatchXML) must be used in such cases

Some changes by Live-XML appear correctly (exactly like the Patch-XML modifications) in [Tuning Inspector](https://github.com/Oops19/TS4-TuningInspector), but they don't affect gameplay.


## Why This Matters
Traits (especially core traits like trait_Adult) and some test tunings are treated differently from most other tunings:
They are:
1. Resolved 
2. Flattened 
3. Cached 
4. Integrated into the interaction graph

All of this happens during instance finalization at startup.
Once this process completes the affordance lists are frozen.
The UI and interaction system will never re-evaluate them.
Zone travel, reloading, and/or re-adding the trait does not rebuild them.

## Live-XML: Usage Limitations

### ❌ Not Supported
Live-XML cannot be used to modify:
* Trait mixer affordances
* Trait super affordances
* Tests which are compiled into complex test objects

Even if the tuning appears updated in TuningInspector the interaction system has already consumed the original data.

### ✅ Supported Use Cases
Live-XML is appropriate for tunings that are evaluated at execution time.

Examples:
* Loot actions
* Tests
* Commodity values
* Thresholds
* Buff tuning
* Conditional logic

## Patch-XML: Recommended for Trait Affordances

### ❌ Not Supported
Patch-XML cannot be used to modify:
* SimData

Modifying tuning values without modifying linked SimData values causes random issues. 

### ✅ Supported
Patch-XML runs during startup, before instance finalization.
This makes it suitable for:
* Adding mixer affordances to traits
* Modifying trait super affordances
* Editing core trait tuning (e.g. trait_Adult)

Because Patch-XML executes early:
* Trait affordances are included before compilation
* Interaction graphs are built correctly
* UI displays the interaction as expected

### ✅ Recommended Usage
Use Patch-XML when modifying:
* Trait affordances
* Core gameplay traits
* Anything affecting interaction availability
