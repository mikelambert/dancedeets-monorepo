# DanceDeets Monorepo

This is a monorepo containing:
- `common/` - Shared JavaScript/TypeScript utilities
- `mobile/` - React Native mobile app
- `server/` - Python/Node.js backend server

## NPM Dependency Compatibility Guidelines

When encountering type errors or compatibility issues between npm packages:

### Anchor Packages
These are our "anchor" packages that define the version constraints. Other packages must be compatible with these:
- **Node.js** - Runtime version
- **React** - UI framework
- **React Native** - Mobile framework (for mobile/)

### Resolution Strategy

1. **Always upgrade libraries** to newer versions that are compatible with our anchors, rather than downgrading anchors or using workarounds.

2. **Check peer dependencies** before upgrading:
   ```bash
   npm view <package>@latest peerDependencies --json
   npm view <package>@latest dependencies --json
   ```

3. **Remove outdated @types packages** when libraries include their own TypeScript definitions:
   - Modern packages (like react-intl v7+) often ship with built-in types
   - Check if `@types/<package>` is needed by looking for `"types"` in the package's package.json
   - Remove from devDependencies if the library has built-in types

4. **Use npm overrides** for transitive dependency conflicts:
   ```json
   {
     "overrides": {
       "@types/react": "^19.0.0"
     }
   }
   ```

### Common Issues

**ReactNode type conflicts** (`bigint is not assignable to ReactNode`):
- This usually means different @types/react versions are in use
- Solution: Upgrade the library to a version that supports your React types version
- Example: react-intl v7+ supports @types/react 16-19

**"Cannot be used as JSX component"**:
- Often caused by React type version mismatches between packages
- Check: `npm ls @types/react` to see all versions installed
- Fix: Add npm overrides or upgrade conflicting packages

### Testing Changes

After fixing compatibility issues, always verify:
```bash
# Check TypeScript compiles
npx tsc --noEmit

# Run unit tests
cd common && npm test
```

## Directory-Specific Guides

See also:
- `server/CLAUDE.md` - Server deployment and Docker instructions
