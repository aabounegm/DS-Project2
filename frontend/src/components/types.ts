export type Endpoint = {
  url: string;
  method: 'get' | 'post' | 'delete' | 'put';
};

export type Endpoints = Record<string, Endpoint>;

export type Item = {
  type: 'file' | 'dir';
  path: string;
  basename: string;
}

export type Icons = Record<string, string>;

export type MyFile = {
  name: string,
  type: string,
  size: number,
  extension?: string,
  preview: string,
};

export type Storage = {
  name: string,
  code: string,
  icon?: string,
};
