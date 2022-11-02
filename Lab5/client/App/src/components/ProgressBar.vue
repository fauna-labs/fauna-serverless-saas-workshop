<template>
    <div class="max-w-full -mt-0 bg-white shadow rounded" v-if="width>0">
      <div class="bg-gray-200 rounded h-1" role="progressbar" 
        :aria-valuenow="width" 
        aria-valuemin="0"
        aria-valuemax="100">
        <div class="bg-green-400 rounded h-1 text-center" :style="`width: ${width}%; transition: width 2s;`">
        </div>
      </div>
    </div>  
</template>

<script>
export default {
  name: 'progress-bar',
  data() {
    return {
      width: 3
    }
  },
  methods: {
    progress() {
      for(let i=0; i<10; i++) {
        setTimeout(
          () => { this.width=(i+1)*10; },
          i*1000 + 1
        );
      }
    },
  },
  mounted() {
    this.width=3;
    this.progress();
  }
}
</script>