<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <div class="d-flex align-center">
        <h1>DS Project 2 - Distributed Filesystem</h1>
      </div>

      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main>
      <FileBrowser
        :storages="remotes"
        :storage="selectedRemote"
      />
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue';
import { Remote } from '@/types';
import FileBrowser from '@/components/FileBrowser.vue';

const remotes: Remote[] = [
  {
    name: 'Local',
    url: 'http://localhost:7507',
    icon: 'mdi-folder-multiple-outline',
  },
  {
    name: 'Remote 1',
    url: 'http://', // TODO: take as input somehow
    icon: 'mdi-cloud',
  },
];

export default Vue.extend({
  name: 'App',
  components: {
    FileBrowser,
  },
  data () {
    return {
      remotes,
      selectedRemote: remotes[0],
    };
  },
});
</script>
