<template>
  <div class="font-medium text-white">
    <button v-if="inactive" type="submit" value="submit"
      :class="`py-2 px-4 ${width} rounded-md bg-indigo-500 opacity-50 cursor-not-allowed`">
      {{ label }}</button>
    <button v-else type="submit" value="submit"
      :class="`py-2 px-4 ${width} rounded-md group relative justify-center border border-transparent bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2`">

      <span class="absolute inset-y-0 left-0 flex items-center pl-3">
        <svg class="h-5 w-5 text-indigo-500 group-hover:text-indigo-400" xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path v-if="icon" fill-rule="evenodd"
            :d="icon"
            clip-rule="evenodd" />
        </svg>
      </span>           

      {{ label }}</button>
  </div>
</template>

<script>
export default {
  name: 'Button',
  props: {
    label: String,
    inactive: {
      type: Boolean,
      default: false
    },
    full: {
      type: Boolean,
      default: false
    },
    icon: String
  },
  data() {
    return {
    }
  },
  computed: {
    width() {
      return this.full? 'w-full' : ''
    }
  }
}
</script>