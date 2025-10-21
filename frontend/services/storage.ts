/**
 * localStorage Service
 * Handles CRUD operations for DynamicElements and SavedOutputs
 */

import { DynamicElement, SavedOutput } from '@/types';

const ELEMENTS_KEY = 'dynamicElements';
const OUTPUTS_KEY = 'savedOutputs';

// ============= Helper Functions =============

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

function getFromStorage<T>(key: string): T[] {
  if (typeof window === 'undefined') return [];

  try {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error(`Error reading from localStorage (${key}):`, error);
    return [];
  }
}

function saveToStorage<T>(key: string, data: T[]): void {
  if (typeof window === 'undefined') return;

  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.error(`Error writing to localStorage (${key}):`, error);
  }
}

// ============= Dynamic Elements CRUD =============

export const createElement = (
  element: Omit<DynamicElement, 'id' | 'createdAt' | 'updatedAt'>
): DynamicElement => {
  const elements = getFromStorage<DynamicElement>(ELEMENTS_KEY);

  const newElement: DynamicElement = {
    ...element,
    id: generateId(),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  elements.push(newElement);
  saveToStorage(ELEMENTS_KEY, elements);

  return newElement;
};

export const getElements = (): DynamicElement[] => {
  return getFromStorage<DynamicElement>(ELEMENTS_KEY);
};

export const getElement = (id: string): DynamicElement | undefined => {
  const elements = getFromStorage<DynamicElement>(ELEMENTS_KEY);
  return elements.find(el => el.id === id);
};

export const updateElement = (
  id: string,
  updates: Partial<Omit<DynamicElement, 'id' | 'createdAt'>>
): DynamicElement | null => {
  const elements = getFromStorage<DynamicElement>(ELEMENTS_KEY);
  const index = elements.findIndex(el => el.id === id);

  if (index === -1) {
    console.error(`Element with id ${id} not found`);
    return null;
  }

  elements[index] = {
    ...elements[index],
    ...updates,
    updatedAt: new Date().toISOString(),
  };

  saveToStorage(ELEMENTS_KEY, elements);
  return elements[index];
};

export const deleteElement = (id: string): boolean => {
  const elements = getFromStorage<DynamicElement>(ELEMENTS_KEY);
  const filteredElements = elements.filter(el => el.id !== id);

  if (filteredElements.length === elements.length) {
    console.error(`Element with id ${id} not found`);
    return false;
  }

  saveToStorage(ELEMENTS_KEY, filteredElements);
  return true;
};

// ============= Saved Outputs CRUD =============

export const saveOutput = (
  output: Omit<SavedOutput, 'id' | 'createdAt'>
): SavedOutput => {
  const outputs = getFromStorage<SavedOutput>(OUTPUTS_KEY);

  const newOutput: SavedOutput = {
    ...output,
    id: generateId(),
    createdAt: new Date().toISOString(),
  };

  outputs.push(newOutput);
  saveToStorage(OUTPUTS_KEY, outputs);

  return newOutput;
};

export const getOutputs = (elementId?: string): SavedOutput[] => {
  const outputs = getFromStorage<SavedOutput>(OUTPUTS_KEY);

  if (elementId) {
    return outputs.filter(output => output.elementId === elementId);
  }

  return outputs;
};

export const getOutput = (id: string): SavedOutput | undefined => {
  const outputs = getFromStorage<SavedOutput>(OUTPUTS_KEY);
  return outputs.find(output => output.id === id);
};

export const getLatestOutput = (elementId: string): SavedOutput | undefined => {
  const outputs = getOutputs(elementId);

  if (outputs.length === 0) return undefined;

  // Sort by createdAt descending and return first
  return outputs.sort((a, b) =>
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  )[0];
};

export const deleteOutput = (id: string): boolean => {
  const outputs = getFromStorage<SavedOutput>(OUTPUTS_KEY);
  const filteredOutputs = outputs.filter(output => output.id !== id);

  if (filteredOutputs.length === outputs.length) {
    console.error(`Output with id ${id} not found`);
    return false;
  }

  saveToStorage(OUTPUTS_KEY, filteredOutputs);
  return true;
};

export const deleteOutputsByElement = (elementId: string): number => {
  const outputs = getFromStorage<SavedOutput>(OUTPUTS_KEY);
  const filteredOutputs = outputs.filter(output => output.elementId !== elementId);
  const deletedCount = outputs.length - filteredOutputs.length;

  saveToStorage(OUTPUTS_KEY, filteredOutputs);
  return deletedCount;
};

// ============= Stats & Analytics =============

export const getStats = () => {
  const elements = getElements();
  const outputs = getOutputs();

  return {
    totalElements: elements.length,
    totalOutputs: outputs.length,
    recentOutputs: outputs
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 5),
  };
};

// ============= Export/Import (Future Enhancement) =============

export const exportElement = (id: string): string | null => {
  const element = getElement(id);
  if (!element) return null;

  return JSON.stringify(element, null, 2);
};

export const importElement = (jsonString: string): DynamicElement | null => {
  try {
    const element = JSON.parse(jsonString);

    // Validate required fields
    if (!element.name || !element.prompt) {
      throw new Error('Invalid element structure');
    }

    // Create new element from imported data (generates new ID)
    return createElement({
      name: element.name,
      description: element.description || '',
      fileType: element.fileType || 'pdf',
      prompt: element.prompt,
      additionalContext: element.additionalContext || [],
    });
  } catch (error) {
    console.error('Error importing element:', error);
    return null;
  }
};
