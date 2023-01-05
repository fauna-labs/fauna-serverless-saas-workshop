<template>
  <div class="flex items-center px-4 -mx-2">
    <img class="object-cover mx-2 rounded-full h-11 w-11"
      src="https://joeschmoe.io/api/v1/{{title}}"
      alt="avatar" />
    <h4 class="mx-0 mt-2 font-medium text-sm text-gray-800 dark:text-gray-200 hover:underline">{{title}}</h4>
  </div>
</template>

<script>
export default {
  name: 'schmoe',
  props: {
    title: String
  }
}
</script>