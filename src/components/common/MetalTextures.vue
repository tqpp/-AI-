<template>
  <div class="metal-texture" :class="[`texture-${type}`, `size-${size}`]">
    <slot></slot>
  </div>
</template>

<script setup>
const props = defineProps({
  // 纹理类型: 'brushed', 'diamond', 'perforated', 'carbon'
  type: {
    type: String,
    default: 'brushed'
  },
  // 尺寸: 'sm', 'md', 'lg', 'full'
  size: {
    type: String,
    default: 'full'
  }
});
</script>

<style lang="scss" scoped>
.metal-texture {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
  
  &.size-sm {
    width: 100px;
    height: 100px;
  }
  
  &.size-md {
    width: 200px;
    height: 200px;
  }
  
  &.size-lg {
    width: 400px;
    height: 400px;
  }
  
  &.size-full {
    width: 100%;
    height: 100%;
  }
  
  // 拉丝金属纹理
  &.texture-brushed {
    background-color: #2D3238;
    background-image: 
      linear-gradient(45deg, rgba(255,255,255,0.07) 25%, transparent 25%),
      linear-gradient(-45deg, rgba(255,255,255,0.07) 25%, transparent 25%),
      linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.07) 75%),
      linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.07) 75%);
    background-size: 4px 4px;
    box-shadow: 
      inset 0 1px 1px rgba(255,255,255,0.1),
      0 1px 3px rgba(0,0,0,0.3);
  }
  
  // 菱形花纹金属
  &.texture-diamond {
    background-color: #3A3F45;
    background-image: 
      linear-gradient(45deg, rgba(0,0,0,0.2) 25%, transparent 25%, transparent 75%, rgba(0,0,0,0.2) 75%),
      linear-gradient(45deg, rgba(0,0,0,0.2) 25%, transparent 25%, transparent 75%, rgba(0,0,0,0.2) 75%);
    background-size: 10px 10px;
    background-position: 0 0, 5px 5px;
    box-shadow: 
      inset 0 1px 1px rgba(255,255,255,0.1),
      0 1px 3px rgba(0,0,0,0.3);
  }
  
  // 穿孔金属板
  &.texture-perforated {
    background-color: #2D3238;
    background-image: radial-gradient(rgba(0,0,0,0.3) 15%, transparent 16%),
      radial-gradient(rgba(0,0,0,0.3) 15%, transparent 16%);
    background-size: 8px 8px;
    background-position: 0 0, 4px 4px;
    box-shadow: 
      inset 0 1px 1px rgba(255,255,255,0.1),
      0 1px 3px rgba(0,0,0,0.3);
  }
  
  // 碳纤维纹理
  &.texture-carbon {
    background-color: #1D1D1D;
    background-image: 
      linear-gradient(45deg, rgba(40,40,40,1) 25%, transparent 25%, transparent 75%, rgba(40,40,40,1) 75%),
      linear-gradient(45deg, rgba(40,40,40,1) 25%, transparent 25%, transparent 75%, rgba(40,40,40,1) 75%);
    background-size: 6px 6px;
    background-position: 0 0, 3px 3px;
    box-shadow: 
      inset 0 1px 1px rgba(255,255,255,0.05),
      0 1px 3px rgba(0,0,0,0.5);
  }
}
</style>