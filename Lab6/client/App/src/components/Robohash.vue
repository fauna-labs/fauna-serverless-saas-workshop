<template>
  <div class="flex flex-col items-center px-4 -mx-2">
    <div>
      <img class="object-cover mx-2 w-17"
        src="https://robohash.org/{{ title }}.png"
        alt="robohash"
        />
    </div>
    <div>
      <h4 class="mx-0 mt-2 font-medium text-sm text-gray-800 dark:text-gray-200 hover:underline">{{title}}</h4>
    </div>
  </div>
</template>

<script>
export default {
  name: 'robohash',
  props: {
    title: String
  }
}
</script>