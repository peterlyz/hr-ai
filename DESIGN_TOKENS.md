# Design Tokens - HR-AI 招聘管理系统

## Typography

### Font Families
```css
--font-display: "Playfair Display", Georgia, serif;  /* 高端衬线，用于标题 */
--font-body: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;  /* 正文阅读 */
--font-mono: "JetBrains Mono", "Courier New", monospace;  /* 代码/数据 */
```

**说明**：
- Display: Playfair Display 传达高端、专业、可信赖感，适合企业级产品
- Body: Inter 虽是常见字体，但在企业管理工具中是最佳选择（可读性高、字重齐全）
- Mono: JetBrains Mono 用于显示简历ID、邮箱等数据

### Type Scale (基于 1.25 比例)
```css
--text-xs: 0.75rem;    /* 12px - 次要标签 */
--text-sm: 0.875rem;   /* 14px - 表格内容、辅助文字 */
--text-base: 1rem;     /* 16px - 正文 */
--text-lg: 1.125rem;   /* 18px - 卡片标题 */
--text-xl: 1.25rem;    /* 20px - 子标题 */
--text-2xl: 1.5rem;    /* 24px - 页面标题 */
--text-3xl: 1.875rem;  /* 30px - 重要标题 */
--text-4xl: 2.25rem;   /* 36px - Hero 标题 */
```

### Line Heights
```css
--leading-tight: 1.25;   /* 标题 */
--leading-normal: 1.5;   /* 正文 */
--leading-relaxed: 1.75; /* 长文本 */
```

### Font Weights
```css
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

---

## Color System

### Brand Colors (使用 OKLCH 色彩空间)
```css
/* 主色：深邃墨蓝 - 专业、可信赖 */
--color-brand: oklch(35% 0.08 250);       /* 主品牌色 */
--color-brand-light: oklch(45% 0.08 250); /* hover 状态 */
--color-brand-dark: oklch(25% 0.08 250);  /* active 状态 */

/* 强调色：琥珀金 - 高端、醒目（用于关键 CTA） */
--color-accent: oklch(65% 0.15 85);
--color-accent-light: oklch(75% 0.15 85);
```

### Neutral Scale
```css
--color-neutral-50: oklch(98% 0 0);    /* 背景 */
--color-neutral-100: oklch(96% 0 0);   /* 卡片背景 */
--color-neutral-200: oklch(90% 0 0);   /* 边框 */
--color-neutral-300: oklch(83% 0 0);   /* 禁用状态 */
--color-neutral-400: oklch(70% 0 0);   /* 占位符 */
--color-neutral-500: oklch(55% 0 0);   /* 次要文字 */
--color-neutral-600: oklch(40% 0 0);   /* 正文 */
--color-neutral-700: oklch(30% 0 0);   /* 标题 */
--color-neutral-800: oklch(20% 0 0);   /* 深色背景 */
--color-neutral-900: oklch(15% 0 0);   /* 最深 */
```

### Semantic Colors
```css
/* 成功 */
--color-success: oklch(60% 0.15 145);
--color-success-bg: oklch(95% 0.05 145);

/* 警告 */
--color-warning: oklch(70% 0.15 65);
--color-warning-bg: oklch(95% 0.05 65);

/* 错误 */
--color-error: oklch(55% 0.18 25);
--color-error-bg: oklch(95% 0.05 25);

/* 信息 */
--color-info: oklch(60% 0.12 240);
--color-info-bg: oklch(95% 0.05 240);
```

### Surface Colors
```css
--color-bg: var(--color-neutral-50);
--color-surface: var(--color-neutral-100);
--color-border: var(--color-neutral-200);
--color-text-primary: var(--color-neutral-700);
--color-text-secondary: var(--color-neutral-500);
--color-text-muted: var(--color-neutral-400);
```

---

## Spacing (8pt Grid System)

```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */

/* 特殊用途 */
--space-section: var(--space-16);  /* 页面区块间距 */
--space-container: var(--space-6); /* 容器内边距 */
```

---

## Border Radius

采用**极端化策略** - luxury-corporate 气质使用克制的圆角：

```css
--radius-none: 0;           /* 完全直角（表格、列表） */
--radius-sm: 0.25rem;       /* 4px - 小元素（标签、徽章） */
--radius-base: 0.5rem;      /* 8px - 按钮、输入框 */
--radius-lg: 0.75rem;       /* 12px - 卡片 */
--radius-xl: 1rem;          /* 16px - 大卡片、模态框 */
--radius-full: 9999px;      /* 圆形（头像） */
```

**原则**：
- 表格/列表：使用 `--radius-none`，保持严肃专业
- 交互元素：使用 `--radius-base`，提升亲和力
- 卡片容器：使用 `--radius-lg`，柔和但不过度

---

## Shadow

**克制使用** - 仅在需要层级区分时使用，模拟真实光源（从上方照射）：

```css
/* 浮起 1 层 - 卡片 */
--shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);

/* 浮起 2 层 - 下拉菜单、弹出层 */
--shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1),
             0 2px 4px -2px rgb(0 0 0 / 0.05);

/* 浮起 3 层 - 模态框、对话框 */
--shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1),
             0 4px 6px -4px rgb(0 0 0 / 0.05);

/* 特殊：内阴影（输入框焦点） */
--shadow-inner: inset 0 2px 4px 0 rgb(0 0 0 / 0.05);
```

**原则**：
- 默认卡片：`--shadow-sm` 或无阴影（用边框区分）
- Hover 状态：不增加阴影（避免过度动效）
- 固定元素：不使用阴影（如侧边栏、顶栏）

---

## Motion & Animation

### Duration
```css
--duration-fast: 150ms;     /* 快速反馈（按钮 hover） */
--duration-base: 250ms;     /* 标准过渡（展开/折叠） */
--duration-slow: 350ms;     /* 慢速过渡（页面切换） */
```

### Easing
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### Animation Principles
1. **仅动画 transform 和 opacity**（避免触发 layout/paint）
2. **支持 prefers-reduced-motion**
3. **Hover 状态**：仅颜色变化 + 轻微位移（≤2px）
4. **Loading 状态**：使用简洁的 spinner，避免骨架屏（信息密度高时会显得混乱）

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Breakpoints (响应式)

```css
--screen-sm: 640px;    /* 移动端 */
--screen-md: 768px;    /* 平板 */
--screen-lg: 1024px;   /* 小屏笔记本 */
--screen-xl: 1280px;   /* 标准桌面 */
--screen-2xl: 1536px;  /* 大屏 */
```

**设计优先级**：
1. **Desktop First (1440px)** - 完整功能
2. Tablet (768px-1024px) - 适度简化
3. Mobile (375px-768px) - 关键功能

---

## Z-Index Scale

```css
--z-base: 0;
--z-dropdown: 1000;
--z-sticky: 1100;
--z-fixed: 1200;
--z-modal-backdrop: 1300;
--z-modal: 1400;
--z-popover: 1500;
--z-tooltip: 1600;
```

---

## Usage Guidelines

### 在 Vue 组件中使用
```vue
<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  line-height: var(--leading-tight);
}
</style>
```

### 在 Tailwind Config 中注入
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: 'oklch(35% 0.08 250)',
        accent: 'oklch(65% 0.15 85)',
        // ... 从上面的 tokens 映射
      },
      fontFamily: {
        display: ['Playfair Display', 'Georgia', 'serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      // ... 其他 tokens
    }
  }
}
```

---

**创建时间**: 2026-06-25  
**版本**: 1.0  
**适用项目**: HR-AI 招聘管理系统
