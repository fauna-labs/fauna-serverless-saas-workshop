<template>
    <div class="max-w-full -mt-0" v-if="width>0">
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
      width: 0
    }
  },
  methods: {
    progress() {
      for(let i=1; i<10; i++) {
        setTimeout(
          () => { this.width=(i+1)*10; },
          i*1000 + 1
        );
      }
    },
  },
  mounted() {
    const comp = this;
    setTimeout(
      () => {
        comp.width=1;
        comp.progress();
      },
      600,
      comp
    );
  }
}
</script>