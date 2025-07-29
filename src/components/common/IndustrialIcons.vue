<template>
  <div class="industrial-icon" :class="[`icon-${type}`, `size-${size}`]">
    <!-- 状态指示灯 -->
    <template v-if="type === 'status-light'">
      <div class="status-light" :class="status">
        <div class="light-glow"></div>
      </div>
    </template>
    
    <!-- 仪表盘 -->
    <template v-else-if="type === 'gauge'">
      <div class="gauge-container">
        <svg viewBox="0 0 120 120" class="gauge">
          <path class="gauge-bg" d="M20,100 A 60,60 0 1,1 100,100" />
          <path class="gauge-fill" :style="{strokeDasharray: `${gaugeValue}, 188.5`}" d="M20,100 A 60,60 0 1,1 100,100" />
          <text x="60" y="80" class="gauge-value">{{ displayValue }}</text>
          <text x="60" y="95" class="gauge-label">{{ label }}</text>
        </svg>
      </div>
    </template>
    
    <!-- 工业按钮 -->
    <template v-else-if="type === 'industrial-button'">
      <div class="ind-button" :class="{active: active}" @click="$emit('click')">
        <div class="button-frame"></div>
        <div class="button-surface">
          <slot></slot>
        </div>
      </div>
    </template>
    
    <!-- 金属面板 -->
    <template v-else-if="type === 'metal-panel'">
      <div class="metal-panel">
        <div class="panel-frame">
          <slot></slot>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  // 图标类型: 'status-light', 'gauge', 'industrial-button', 'metal-panel'
  type: {
    type: String,
    default: 'status-light'
  },
  // 尺寸: 'sm', 'md', 'lg'
  size: {
    type: String,
    default: 'md'
  },
  // 状态灯状态: 'normal', 'warning', 'error', 'inactive'
  status: {
    type: String,
    default: 'normal'
  },
  // 仪表盘值 (0-100)
  value: {
    type: Number,
    default: 0
  },
  // 仪表盘最大值
  max: {
    type: Number,
    default: 100
  },
  // 仪表盘标签
  label: {
    type: String,
    default: '%'
  },
  // 按钮是否激活
  active: {
    type: Boolean,
    default: false
  }
});

const gaugeValue = computed(() => {
  // 计算仪表盘填充值 (最大188.5)
  return (props.value / props.max) * 188.5;
});

const displayValue = computed(() => {
  // 显示值
  return Math.round(props.value);
});

defineEmits(['click']);
</script>

<style lang="scss" scoped>
.industrial-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  
  &.size-sm {
    width: 24px;
    height: 24px;
  }
  
  &.size-md {
    width: 48px;
    height: 48px;
  }
  
  &.size-lg {
    width: 80px;
    height: 80px;
  }
}

/* 状态指示灯样式 */
.status-light {
  position: relative;
  width: 80%;
  height: 80%;
  border-radius: 50%;
  background: #333;
  box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
  border: 2px solid #444;
  overflow: hidden;
  
  &.normal {
    background: linear-gradient(145deg, #1a9a3c, #21BA45);
    
    .light-glow {
      background: radial-gradient(circle, rgba(33,186,69,0.8) 0%, rgba(33,186,69,0) 70%);
    }
  }
  
  &.warning {
    background: linear-gradient(145deg, #d9a730, #F2C037);
    
    .light-glow {
      background: radial-gradient(circle, rgba(242,192,55,0.8) 0%, rgba(242,192,55,0) 70%);
    }
  }
  
  &.error {
    background: linear-gradient(145deg, #a30012, #C10015);
    
    .light-glow {
      background: radial-gradient(circle, rgba(193,0,21,0.8) 0%, rgba(193,0,21,0) 70%);
    }
  }
  
  &.inactive {
    background: linear-gradient(145deg, #3a3f45, #4A4E54);
    
    .light-glow {
      display: none;
    }
  }
  
  .light-glow {
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    opacity: 0.7;
    animation: pulse 2s infinite;
  }
}

/* 仪表盘样式 */
.gauge-container {
  width: 100%;
  height: 100%;
}

.gauge {
  width: 100%;
  height: 100%;
  
  .gauge-bg {
    fill: none;
    stroke: #3A3F45;
    stroke-width: 12;
    stroke-linecap: round;
  }
  
  .gauge-fill {
    fill: none;
    stroke: var(--industrial-blue);
    stroke-width: 12;
    stroke-linecap: round;
    transition: stroke-dasharray 0.5s ease;
  }
  
  .gauge-value {
    font-size: 24px;
    font-weight: bold;
    text-anchor: middle;
    fill: #fff;
  }
  
  .gauge-label {
    font-size: 14px;
    text-anchor: middle;
    fill: #aaa;
  }
}

/* 工业按钮样式 */
.ind-button {
  position: relative;
  width: 100%;
  height: 100%;
  cursor: pointer;
  user-select: none;
  
  .button-frame {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: #2D3238;
    border: 2px solid #3A3F45;
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
  }
  
  .button-surface {
    position: absolute;
    top: 4px;
    left: 4px;
    right: 4px;
    bottom: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #4E5560, #3A3F45);
    border-radius: 4px;
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
    transition: all 0.1s ease;
  }
  
  &.active .button-surface {
    top: 6px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.3);
    background: linear-gradient(145deg, #3A3F45, #4E5560);
  }
  
  &:hover .button-surface {
    background: linear-gradient(145deg, #5A6270, #4A4E54);
  }
}

/* 金属面板样式 */
.metal-panel {
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #3A3F45, #2D3238);
  border: 1px solid #4A4E54;
  border-radius: 4px;
  box-shadow: 
    inset 0 1px 1px rgba(255,255,255,0.1),
    0 1px 3px rgba(0,0,0,0.3);
  
  .panel-frame {
    width: 100%;
    height: 100%;
    padding: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

@keyframes pulse {
  0% {
    opacity: 0.7;
  }
  50% {
    opacity: 0.3;
  }
  100% {
    opacity: 0.7;
  }
}
</style>