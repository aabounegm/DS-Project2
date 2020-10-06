<template>
  <v-card flat tile width="250" min-height="380" class="d-flex flex-column folders-tree-card">
    <div class="grow scroll-x">
      <v-treeview
        :open="open"
        :active="active"
        :items="items"
        :search="filter"
        :load-children="readFolder"
        @update:active="activeChanged"
        item-key="path"
        item-text="name"
        dense
        activatable
        transition
        class="folders-tree"
      >
        <template v-slot:prepend="{ item, open }">
          <v-icon
            v-if="item.is_directory"
          >{{ open ? 'mdi-folder-open-outline' : 'mdi-folder-outline' }}</v-icon>
          <v-icon v-else>{{ icons[item.extension] || icons['other'] }}</v-icon>
        </template>
        <template v-slot:label="{ item }">
          {{item.name}}
          <v-btn
            icon
            v-if="item.is_directory"
            @click.stop="readFolder(item)"
            class="ml-1"
          >
            <v-icon class="pa-0 mdi-18px" color="grey lighten-1">mdi-refresh</v-icon>
          </v-btn>
        </template>
      </v-treeview>
    </div>
    <v-divider></v-divider>
    <v-toolbar dense flat class="shrink">
      <v-text-field
        solo
        flat
        hide-details
        label="Filter"
        v-model="filter"
        prepend-inner-icon="mdi-filter-outline"
        class="ml-n3"
      ></v-text-field>
      <v-tooltip top>
        <template v-slot:activator="{ on }">
          <v-btn icon @click="init" v-on="on">
            <v-icon>mdi-collapse-all-outline</v-icon>
          </v-btn>
        </template>
        <span>Collapse All</span>
      </v-tooltip>
    </v-toolbar>
  </v-card>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue';
import { TreeItem, Icons } from '@/types';

export default Vue.extend({
  props: {
    icons: {
      type: Object as PropType<Icons>,
    },
    path: {
      type: String,
    },
    baseUrl: {
      type: String,
    },
    refreshPending: {
      type: Boolean,
    },
  },
  data () {
    return {
      open: [] as string[],
      active: [] as string[],
      items: [] as TreeItem[],
      filter: '',
    };
  },
  methods: {
    init () {
      this.open = [];
      this.items = [];
      // set default files tree items (root item) in nextTick.
      // Otherwise this.open isn't cleared properly (due to syncing perhaps)
      Vue.nextTick().then(() => {
        this.items = [{
          is_directory: true,
          name: 'root',
          path: '/',
          children: [],
        }];
      });
      if (this.path !== '') {
        this.$emit('path-changed', '');
      }
    },
    async readFolder (item: TreeItem) {
      if (!item.is_directory) {
        return;
      }
      this.$emit('loading', true);

      const url = `${this.baseUrl}/dir${item.path}`;

      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw await response.text();
        }
        const data: TreeItem[] = await response.json();
        item.children = data.map(item => {
          if (item.is_directory) {
            item.children = [];
          }
          return item;
        });
      } catch (error) {
        console.error(error);
        alert('An error occured. Check the console');
      }

      this.$emit('loading', false);
    },
    activeChanged (active: string[]) {
      this.active = active;
      let path = '';
      if (active.length > 0) {
        path = active[0];
      }
      if (this.path !== path) {
        this.$emit('path-changed', path);
      }
    },
    findItem (path: string) {
      const stack: TreeItem[] = [];
      stack.push(this.items[0]);
      while (stack.length > 0) {
        const node = stack.pop();
        if (node == null) {
          break;
        }
        if (node.path === path) {
          return node;
        } else if (node.is_directory && node.children?.length > 0) {
          for (let i = 0; i < node.children.length; i++) {
            stack.push(node.children[i]);
          }
        }
      }
      return null;
    },
  },
  watch: {
    baseUrl () {
      this.init();
    },
    path () {
      this.active = [this.path];
      if (!this.open.includes(this.path)) {
        this.open.push(this.path);
      }
    },
    async refreshPending (newValue: boolean, _oldValue: boolean) {
      if (!newValue) {
        return;
      }
      const item = this.findItem(this.path);
      if (!item?.is_directory) {
        return;
      }
      await this.readFolder(item);
      this.$emit('refreshed');
    },
  },
  created () {
    this.init();
  },
});
</script>

<style lang="scss" scoped>
.folders-tree-card {
  height: 100%;

  .scroll-x {
    overflow-x: auto;
  }

  ::v-deep .folders-tree {
    width: fit-content;
    min-width: 250px;

    .v-treeview-node {
      cursor: pointer;

      &:hover {
        background-color: rgba(0, 0, 0, 0.02);
      }
    }
  }
}
</style>
