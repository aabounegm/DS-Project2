<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <div class="d-flex align-center">
        <h1>DS Project 2 - Distributed Filesystem</h1>
      </div>

      <v-spacer></v-spacer>
    </v-app-bar>

    <v-main>
      <v-row no-gutters>
        <v-col cols="3">
          <v-list>
            <v-subheader>Remotes</v-subheader>
            <v-list-item-group>
              <v-list-item v-for="remote in remotes" :key="remote.url">
                <v-list-item-icon>
                  <v-icon>{{ remote.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ remote.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ remote.url }}</v-list-item-subtitle>
                </v-list-item-content>
                <v-list-item-action>
                  <v-btn icon @click="remove(remote.url)">
                    <v-icon color="error">
                      mdi-delete
                    </v-icon>
                  </v-btn>
                </v-list-item-action>
              </v-list-item>
            </v-list-item-group>
          </v-list>
          <v-divider />
          <div class="px-4" style="display: grid;">
            <v-text-field autocomplete="off" v-model="name" label="Name" hint="Name of remote server" />
            <v-text-field v-model="url" label="Address" hint="http://10.0.0.1" />
            <v-btn fab class="ml-auto" color="pink" :dark="!!name && !!url" @click="add" :disabled="!name || !url">
              <v-icon>mdi-plus</v-icon>
            </v-btn>
          </div>
        </v-col>
        <v-col cols="9">
          <FileBrowser
            :storages="remotes"
          />
        </v-col>
      </v-row>
    </v-main>
  </v-app>
</template>

<script lang="ts">
import Vue from 'vue';
import { Remote } from '@/types';
import FileBrowser from '@/components/FileBrowser.vue';

export default Vue.extend({
  name: 'App',
  components: {
    FileBrowser,
  },
  data () {
    return {
      remotes: [
        {
          name: 'AWS',
          url: 'http://107.23.166.30',
          icon: 'mdi-cloud',
        },
        {
          name: 'Local',
          url: 'http://localhost:7507',
          icon: 'mdi-folder-multiple-outline',
        },
      ] as Remote[],
      name: '',
      url: 'http://',
    };
  },
  methods: {
    add () {
      const { name, url } = this;
      if (name === '' || url === '') {
        return;
      }
      if (this.remotes.find(r => r.url === url) != null) {
        alert('Remote already exists');
        return;
      }
      this.remotes.push({
        name,
        url,
        icon: 'mdi-cloud',
      });
      this.name = '';
      this.url = 'http://';
    },
    remove (url: string) {
      const index = this.remotes.findIndex(r => r.url === url);
      if (index === -1) {
        return;
      }
      this.remotes.splice(index, 1);
    },
  },
});
</script>
